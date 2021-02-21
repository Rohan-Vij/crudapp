# Web handler (Flask) import
from flask import Flask, Blueprint, render_template

# Importing OS
import os

# Initializing Flask App
app = Flask(__name__)

# Importing and initializing API blueprint
from api import api
app.register_blueprint(api)

# Importing and initializing user blueprint
from user import user
app.register_blueprint(user)

# Importing and initializing user management blueprint
from mgmt import mgmt
app.register_blueprint(mgmt)

app.secret_key = os.urandom(24)

@app.errorhandler(404)
def page_not_found(e):
  return render_template('error/404.html'), 404

@app.errorhandler(500)
def server_error(e):
  return render_template('error/500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)