# server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

app = Flask(__name__)
CORS(app)

uri = "mongodb+srv://timtujuh:vV2WEXiqjSTmPevl@clustertimtujuh.8p34h.mongodb.net/?retryWrites=true&w=majority&appName=ClusterTimTujuh"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["TimTujuhDatabase"]
collection = db["MySensorData"]

@app.route("/sensor", methods=["POST"])
def receive_data():
    try:
        data = request.json
        required_keys = {"humidity", "temperature", "motion", "ldr"}
        if not all(key in data and isinstance(data[key], (int, float)) for key in required_keys):
            return jsonify({"error": "Format data tidak valid!"}), 400

        data["timestamp"] = datetime.utcnow()
        collection.insert_one(data)

        return jsonify({"message": "Data berhasil disimpan"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/sensor", methods=["GET"])
def get_data():
    data = list(collection.find({}, {"_id": 0}).sort("timestamp", -1))
    return jsonify(data), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)