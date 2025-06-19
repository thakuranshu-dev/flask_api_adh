from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from pymongo import MongoClient
import gridfs
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.environ.get('MONGO_URL')

app = Flask(__name__)
CORS(app)

# MongoDB connection (adjust as needed)
client = MongoClient(uri)
db = client['collegeApp']
fs = gridfs.GridFS(db)

@app.route('/upload_profile_photo', methods=['POST'])
def upload_profile_photo():
    if 'photo' not in request.files or 'uid' not in request.form:
        return jsonify({"error": "Photo or userID not provided"}), 400

    file = request.files['photo']
    uid = request.form['uid']

    # Delete old profile photo if it exists for the user
    existing = db.fs.files.find_one({'metadata.uid': uid})
    if existing:
        fs.delete(existing['_id'])

    # Store file with userID in metadata
    file_id = fs.put(file, filename=file.filename, content_type=file.content_type, metadata={'uid': uid})

    return jsonify({
        "message": "Upload successful",
        "file_id": str(file_id),
        "uid": uid
    }), 200

@app.route('/get_profile_photo/<uid>', methods=['GET'])
def get_profile_photo(uid):
    file_doc = db.fs.files.find_one({'metadata.uid': uid})
    if file_doc:
        file = fs.get(file_doc['_id'])
        return send_file(file, mimetype=file.content_type)
    else:
        return jsonify({"error": "Profile photo not found for this user"}), 404

if __name__ == '__main__':
    app.run(port=5000, debug=True)
