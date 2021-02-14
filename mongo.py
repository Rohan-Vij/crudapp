# mongo.py

# Web handler (Flask) import
from flask import Flask, jsonify, request, render_template, send_file, redirect, url_for

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
fs = gridfs.GridFS(db, collection="fs")
gs = gridfs.GridFS(db, collection="gs")

# Initializing Flask App
app = Flask(__name__)

@app.route('/art', methods=['GET'])
def get_art():
    output = []
    for s in collection.find():
        b = gs.get(s["image"]).read()
        byte_data = b64encode(b).decode("utf-8")
        output.append({'_id': str(s["_id"]), 'name': s['name'], 'artist': s['artist'], 'type': s['type'], 'image_data': str(byte_data)[:20] + "...", "image_id": str(s["image"])})
    return jsonify({'result': output})


@app.route('/art/<key>/<value>', methods=['GET'])
def search(key, value):
    if db.art.count_documents({key: value}, limit = 1) != 0:    
        output = [{item: str(data[item]) for item in data.keys()} for data in collection.find({key: value})]
        return jsonify({'result': output})
    else:
        return jsonify({'result': "nothing found"})

@app.route('/art/data/<id>')
def data(id):
    output = []
    for s in collection.find({"_id": ObjectId(id)}):
        b = gs.get(s["image"]).read()
        byte_data = b64encode(b).decode("utf-8")
        output.append({'_id': str(s["_id"]), 'name': s['name'], 'artist': s['artist'], 'type': s['type'], 'image_data': str(byte_data)[:20] + "...", "image_id": str(s["image"])})
    return jsonify({'result': output})

@app.route('/art/picture/<id>')
def picture(id):
    picture = gs.get(ObjectId(id)).read()

    return send_file(io.BytesIO(picture), mimetype = 'image/jpeg', as_attachment = False, attachment_filename= f'{id}.jpg')

@app.route('/art/view', methods=['GET'])
def view_art():
    output = []
    for s in collection.find():
        read = gs.get(s["image"]).read()
        byte_data = b64encode(read).decode("utf-8")
        output.append({'_id': str(s["_id"]), 'name': s['name'], 'artist': s['artist'], 'type': s['type'], 'image_data': byte_data, 'image_id': str(s["image"])})
    
    return render_template("showall.html", data=output)     

@app.route('/art/insert', methods=["GET", "POST"])
def insertToDatabase():
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

        # data = gs.get(a).read()
        # with open(f"images/{name}.jpg", "wb")  as outfile:   
        #     outfile.write(data)

        return render_template("add.html")
    else:
        return render_template("add.html")   

@app.route('/art/view/delete', methods=["POST"])
def deleteFromDatabase():
    data = request.form["data"]
    img = request.form["img"]


    db.art.delete_one({'_id': ObjectId(data)})
    db["gs.chunks"].delete_many({'files_id': ObjectId(img)})
    db["gs.files"].delete_one({'_id': ObjectId(img)})

    return redirect(url_for("view_art"))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)