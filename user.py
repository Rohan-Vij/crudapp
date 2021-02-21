# Web handler (Flask) import
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for, session, g, Blueprint

# Database (MongoDB) imports
from pymongo import MongoClient
from bson.objectid import ObjectId
from base64 import b64encode
import gridfs
import io

# Requests + json import to access other parts of the application. 
import requests, json

# Initializing connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["restdb"]
collection = db["art"]

# Initializing connection to MongoDB image collections
# https://docs.mongodb.com/manual/core/gridfs/
gs = gridfs.GridFS(db, collection="gs")

user = Blueprint('user', __name__)

@user.route('/art/view', methods=['GET'])
def view():
    """ View all the data in the DB with a styled webpage. """
    if "user" in session:
        output = []
        for s in collection.find():
            read = gs.get(s["image"]).read()
            byte_data = b64encode(read).decode("utf-8")
            output.append({'_id': str(s["_id"]), 'name': s['name'], 'artist': s['artist'], 'type': s['type'], 'image_data': byte_data, 'image_id': str(s["image"])})
        
        return render_template("showall.html", data=output)    
    return render_template("login.html", message="Please log in before continuing.", style="warning")


@user.route('/art/view/insert', methods=["GET", "POST"])
def insert():
    """ Insert a piece of art (metadata and image) into the DB from a styled webpage. """
    if "user" in session:
        if request.method == 'POST':
            name = request.form["name"]
            artist = request.form["artist"]
            type_of_art = request.form["type"]
            img = request.files["img"]
            a = gs.put(img, encoding='utf-8')

            rec = {"name": name,
                    "artist": artist,
                    "type": type_of_art,
                    "image": a}

            db.art.insert_one(rec)

            # Use the code below if you wish to save the image to your system
            # data = gs.get(a).read()
            # with open(f"images/{name}.jpg", "wb")  as outfile:   
            #     outfile.write(data)

            return redirect(url_for("user.view"))
        return redirect(url_for("user.view"))
    return render_template("login.html", message="Please log in before continuing.", style="warning")

@user.route('/art/view/delete', methods=["POST"])
def delete():
    """ Delete a piece of art (metadata and image) from the DB from a styled webpage. """
    if "user" in session:
        data = request.form["data"]
        img = request.form["img"]


        db.art.delete_one({'_id': ObjectId(data)})
        db["gs.chunks"].delete_many({'files_id': ObjectId(img)})
        db["gs.files"].delete_one({'_id': ObjectId(img)})

        return redirect(url_for("user.view"))
    return render_template("login.html", message="Please log in before continuing.", style="warning")    

@user.route('/art/view/update', methods=["POST"])
def update():
    """ Update a piece of art (metadata only) in the DB from a styled webpage. """
    if "user" in session:
        update_id = request.form["update_id"]
        update_name = request.form["update_name"]
        update_artist = request.form["update_artist"]
        update_type = request.form["update_type"]

        myquery = {'_id': ObjectId(update_id)}
        newvalues = {"$set": {"name": update_name, "artist": update_artist, "type": update_type}}

        db.art.update_one(myquery, newvalues)

        return redirect(url_for("user.view"))
    return render_template("login.html", message="Please log in before continuing.", style="warning")