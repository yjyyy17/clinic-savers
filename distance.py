from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

import invokes 
import json

app = Flask(__name__)
CORS(app)

api_key = "AIzaSyC1hytlrSzRCAMd4LK-A0hzQ85IoVZIJpg"

@app.route("/checkDist", methods = ["POST"])
def get_distance():
    data = request.get_json()
    
    patient = data["patientAddress"]
    clinics = data["clinics"]

    clinic_path = ""
    for postal in clinics:
        clinic_path += "Singapore " + postal + "%7C"
    clinic_path = clinic_path[:-3]

    url = "https://maps.googleapis.com/maps/api/distancematrix/json?destinations=" + clinic_path + "&origins=Singapore " + patient + "&region=sg&key=" + api_key
    result = invokes.invoke_http(url,"GET")
    
    if result["origin_addresses"] != [""]:
        return jsonify(
            {
                "code": 200,
                "data": result
            }
        )

    return jsonify(
        { 
            "code": 404,
            "message": "Patient Postal Code not found"
        }
    ), 404    

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
