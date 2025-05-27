from flask import Flask, jsonify
from flask_pymongo import PyMongo
import requests
import schedule
import time
import threading
from datetime import datetime
import os

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")


mongo = PyMongo(app)

WAQI_URL = "https://api.waqi.info/feed/A499747/?token=866a9b35170c510c9c82eeb3f158476e17a4c214"

def fetch_and_store():
    try:
        response = requests.get(WAQI_URL)
        data = response.json()
        if data['status'] != 'ok':
            print("❌ WAQI error")
            return
        record = {
            "timestamp": datetime.utcnow(),
            "aqi": data["data"]["aqi"],
            "iaqi": data["data"]["iaqi"]
        }
        mongo.db.measurements.insert_one(record)
        print("✅ Datos guardados:", record["timestamp"])
    except Exception as e:
        print("⚠️ Error al obtener datos:", e)

def start_scheduler():
    schedule.every(5).minutes.do(fetch_and_store)
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/historico', methods=['GET'])
def get_historico():
    data = list(mongo.db.measurements.find().sort("timestamp", -1).limit(100))
    for d in data:
        d['_id'] = str(d['_id'])
    return jsonify(data)

@app.route('/')
def home():
    return "✅ Backend Flask activo en Render"

if __name__ == '__main__':
    threading.Thread(target=start_scheduler, daemon=True).start()
    app.run(host='0.0.0.0', port=3000)
