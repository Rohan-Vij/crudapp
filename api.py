# Web handler (Flask) import
from flask import Flask, jsonify, request, send_file, Blueprint

# Database (MongoDB) imports
from pymongo import MongoClient
from bson.objectid import ObjectId
from base64 import b64encode
import gridfs
import io

# Initializing connection to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client["restdb"]
collection = db["art"]

# Initializing connection to MongoDB image collections
# https://docs.mongodb.com/manual/core/gridfs/
gs = gridfs.GridFS(db, collection="gs")

api = Blueprint('api', __name__)


@api.route('/art', methods=['GET'])
def get_art():
    """ Return data from the DB in the format JSON. """
    output = []
    for s in collection.find():
        b = gs.get(s["image"]).read()
        byte_data = b64encode(b).decode("utf-8")
        output.append({'_id': str(s["_id"]), 'name': s['name'], 'artist': s['artist'], 'type': s['type'], 'image_data': str(
            byte_data)[:20] + "...", "image_id": str(s["image"])})
    return jsonify({'result': output})


@api.route('/art/<key>/<value>', methods=['GET'])
def search(key, value):
    """ Return a specific key/value pair from the DB. Returns a maximum of one result (the first one found). """
    if db.art.count_documents({key: value}, limit=1) != 0:
        output = [{item: str(data[item]) for item in data.keys()}
                  for data in collection.find({key: value})]
        return jsonify({'result': output})
    else:
        return jsonify({'result': "nothing found"})


@api.route('/art/data/<id>')
def data(id):
    """ Returns all the art metadata associated with the given id. """
    output = []
    for s in collection.find({"_id": ObjectId(id)}):
        b = gs.get(s["image"]).read()
        byte_data = b64encode(b).decode("utf-8")
        output.append({'_id': str(s["_id"]), 'name': s['name'], 'artist': s['artist'], 'type': s['type'], 'image_data': str(
            byte_data)[:20] + "...", "image_id": str(s["image"])})
    return jsonify({'result': output})


@api.route('/art/picture/<id>')
def picture(id):
    """ Returns the image associated with the given id. """
    picture = gs.get(ObjectId(id)).read()

    return send_file(io.BytesIO(picture), mimetype='image/jpeg', as_attachment=False, attachment_filename=f'{id}.jpg')
