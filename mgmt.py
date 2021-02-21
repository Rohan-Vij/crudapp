# Web handler (Flask) import
from flask import Flask, jsonify, request, render_template, redirect, url_for, session, g, Blueprint

# Database (MongoDB) imports
from pymongo import MongoClient
from bson.objectid import ObjectId
from base64 import b64encode
import gridfs
import io

# Initializing connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["restdb"]

# Link expiration
from itsdangerous import URLSafeTimedSerializer
s = URLSafeTimedSerializer('basingse')

# Email sending packages
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Environment variables
from dotenv import load_dotenv
load_dotenv()

# Getting environment variables
import os
email_name = os.getenv("NAME")
email_domain = os.getenv("DOMAIN")
email_password = os.getenv("PASSWORD")

# Printing environment variables
print("Email name:", email_name)
print("Email domain:", email_domain)
print("Email password:", email_password)

mgmt = Blueprint('mgmt', __name__)

@mgmt.route('/art/login', methods=['GET', 'POST'])
def login():
    """ Login to the application with previously created credentials stored in the database. """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['pass']
        document = {"email": email, "password": password}
        user_document = {"email": email}
        verified_document = {"email": email, "password": password, "verified": True}

        if db.users.find(user_document).count() > 0:
            if db.users.find(document).count() > 0:
                if db.users.find(verified_document).count() > 0:
                    session['user'] = email
                    return redirect(url_for("user.view"))
                else:
                    send_email(email)
                    return render_template("login.html", message="Make sure your account has been verified! We resent your verification email.", style="warning")
            else:
                return render_template("login.html", message="Incorrect password.", style="danger")
        else:
            return render_template("login.html", message="An account with that email address does not exist.", style="danger")
    return render_template("login.html")

@mgmt.route("/art/signup", methods=["GET", "POST"])
def signup():
    """ Create credentials stored in the database to later login to the application. """
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['pass']

        query = {"email": email}

        # Checking if the entered email exists
        if db.users.find(query).count() > 0:
            return render_template("signup.html", message="That email address already has an account.")
        else:
            document = {"name": name, "email": email, "password": password, "verified": False}
            send_email(email)
            db.users.insert_one(document)

            return render_template("signup.html", message=f"Your account has been created! Check your email to verify your account and get started! The link expires in an hour!", style="success")
    return render_template("signup.html")

@mgmt.route('/art/verify/<token>', methods=["GET"])
def verify(token):
    """ Verify the account of a user when they access a link. """
    email = request.args.get('email')
    url = s.loads(token, salt='email-confirm', max_age=3600)
    myquery = {"email": email}
    newvalues = {"$set": {"verified": True}}

    db.users.update_one(myquery, newvalues)

    return render_template("login.html", message="Email confirmed. You can log in now!", style="success")

def send_email(email):
    """ Generate a verification link and send an email to verify a user's account. """
    token = s.dumps(email, salt='email-confirm')
    URL = f"http://192.168.1.115:5001/art/verify/{token}?email={email}"

    # me == my email address
    # you == recipient's email address
    me = f"{email_name}@{email_domain}"
    target = email

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "Verification"
    msg['From'] = me
    msg['To'] = target

    # Create the body of the message (a plain-text and an HTML version).
    text = f"Hi!\nClick on the following link to verify your account:\n{URL}"
    html = f"""\
    <html>
      <head></head>
      <body>
        <p>Hi!<br>
           Click on <a href="{URL}">this</a> link to verify your account.
        </p>
      </body>
    </html>
    """

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    # Send the message via local SMTP server.
    mail = smtplib.SMTP('smtp.gmail.com', 587)

    mail.ehlo()

    mail.starttls()

    mail.login(email_name, email_password)
    mail.sendmail(me, target, msg.as_string())
    mail.quit()

@mgmt.route('/art/user', methods=['GET'])
def current_user():     
    """ Print the current user. Currently used for testing purposes. """
    if "user" in session:
        return jsonify({"result": {"current_user_email": g.user}})
    return render_template("login.html", message="Please log in before continuing.", style="warning")

@mgmt.route("/art/signout")
def signout():
    """ Lets the user sign out of the application. """
    if "user" in session:
        session.clear()
        return render_template("login.html", message="Successfully logged out!", style="success")
    return render_template("login.html", message="Make sure you are logged in!", style="warning")


@mgmt.before_request
def before_request():
    """ Keep the user's login stored as they travel webpages. """
    g.user = None
    if "user" in session:
        g.user = session['user']    
