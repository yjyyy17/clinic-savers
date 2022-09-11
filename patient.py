from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app)  

class Patient(db.Model):
    __tablename__ = 'patient'
    nric = db.Column(db.String(9), nullable=False, primary_key=True)
    patientName = db.Column(db.String(64), nullable=False)
    mobileNumber = db.Column(db.String(8), nullable=False)
    postalCode = db.Column(db.String(6), nullable=False)
    address = db.Column(db.String(128), nullable=False)

    def __init__(self, nric, patientName, mobileNumber, postalCode, address):
        self.nric = nric
        self.patientName = patientName
        self.mobileNumber = mobileNumber
        self.postalCode = postalCode
        self.address = address
        
    def json(self):
        return {"patientName": self.patientName, "nric": self.nric, "mobileNumber": self.mobileNumber, "postalCode": self.postalCode, "address": self.address}


@app.route("/patient")
def get_all():
    patientlist = Patient.query.all()
    if len(patientlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "patient": [patient.json() for patient in patientlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no patients."
        }
    ), 404


@app.route("/patient/<string:nric>")
def find_by_nric(nric):
    patient = Patient.query.filter_by(nric=nric).first()

    if patient:
        return jsonify(
            {
                "code": 200,
                "data": patient.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Patient not found."
        }
    ), 404


@app.route("/patient/<string:nric>", methods=['POST'])
def create_patient(nric):
    if (Patient.query.filter_by(nric=nric).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "nric": nric
                },
                "message": "Patient already exists."
            }
        ), 400

    data = request.get_json()

    patient = Patient(nric, **data)

    try:
        db.session.add(patient)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "nric": nric
                },
                "message": "An error occurred creating the patient account."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": patient.json()
        }
    ), 201


@app.route("/patient/<string:nric>", methods=['PUT'])
def update_patient(nric):
    patient = Patient.query.filter_by(nric=nric).first()
    if patient:
        data = request.get_json()
        if data['patientName']:
            patient.patientName = data['patientName']
        if data['mobileNumber']:
            patient.mobileNumber = data['mobileNumber'] 
        if data['address']:
            patient.address = data['address']     
        if data['postalCode']:
            patient.postalCode = data['postalCode'] 
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": patient.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "nric": nric
            },
            "message": "Patient not found."
        }
    ), 404


@app.route("/patient/<string:nric>", methods=['DELETE'])
def delete_patient(nric):
    patient = Patient.query.filter_by(nric=nric).first()
    if patient:
        db.session.delete(patient)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "nric": nric
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "nric": nric
            },
            "message": "Patient not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
