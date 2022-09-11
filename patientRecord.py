import os, sys
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class PatientRecord(db.Model):
    __tablename__ = 'patientRecord'

    patientRecordId = db.Column(db.Integer, primary_key=True, nullable=False)
    nric = db.Column(db.String(9), primary_key=True, nullable=False)
    clinicId = db.Column(db.Numeric(3), primary_key=True, nullable=False)
    drugName = db.Column(db.String(128), primary_key=True, nullable=False)
    prescribeQuantity = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(64), primary_key=True, nullable=False)
    time = db.Column(db.String(64), primary_key=True, nullable=False)

    def __init__(self, patientRecordId, nric, clinicId, drugName, prescribeQuantity, date, time):
        self.patientRecordId = patientRecordId
        self.nric = nric
        self.clinicId = clinicId
        self.drugName = drugName
        self.prescribeQuantity = prescribeQuantity
        self.date = date
        self.time = time

    def json(self):
        return {"patientRecordId":self.patientRecordId, "nric": self.nric, "clinicId": self.clinicId, "drugName": self.drugName, "prescribeQuantity": self.prescribeQuantity, "date": self.date, "time": self.time}


@app.route("/patientRecord")
def get_all_patient_record():
    patient_record_list = PatientRecord.query.all()
    if len(patient_record_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "PatientRecords": [record.json() for record in patient_record_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no patient records."
        }
    ), 404

@app.route("/patientRecord/<string:clinicId>")
def find_patient_record_by_clinic(clinicId):
    record_list = PatientRecord.query.filter_by(clinicId=clinicId).all()
    if len(record_list):
        return jsonify(
            {
                "code": 200,
                "data":{
                    "PatientRecords": [record.json() for record in record_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Patient record not found."
        }
    ), 404

@app.route("/patientRecord/clinic/<string:nric>/<string:clinicId>")
def find_patient_record_by_nric_and_clinic(nric,clinicId):
    record_list = PatientRecord.query.filter_by(nric=nric,clinicId=clinicId).all()
    if len(record_list):
        return jsonify(
            {
                "code": 200,
                "data":{
                    "PatientRecords": [record.json() for record in record_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Patient record not found."
        }
    ), 404

@app.route("/patientRecord/<string:nric>/<string:clinicId>/<string:drugName>/<string:date>/<string:time>")
def find_patient_record_by_nric_clinic_drug_date_time(nric,clinicId,drugName,date,time):
    record = PatientRecord.query.filter_by(nric=nric,clinicId=clinicId,drugName=drugName,date=date,time=time).first()
    if record:
        return jsonify(
            {
                "code": 200,
                "data": record.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Patient record not found."
        }
    ), 404


@app.route("/patientRecord/<string:nric>", methods=['POST'])
def create_patient_record(nric):
    patient_record_list = PatientRecord.query.all()
    new_id = len(patient_record_list) + 1
    data = request.get_json()
    record = PatientRecord(new_id,nric, **data)
    print(record)

    try:
        db.session.add(record)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "nric": nric
                },
                "message": "An error occurred creating the patient record."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": record.json()
        }
    ), 201


@app.route("/patientRecord/<string:nric>/<string:clinicId>/<string:drugName>/<string:date>/<string:time>", methods=['PUT'])
def update_patient_record(nric,clinicId,drugName,date,time):
    record = PatientRecord.query.filter_by(nric=nric,clinicId=clinicId,drugName=drugName,date=date,time=time).first()
    if record:
        data = request.get_json()
        if "nric" in data:
            record.nric = data['nric']
        if "drugName" in data:
            record.drugName = data['drugName']
        if "prescribeQuantity" in data:
            record.prescribeQuantity = data['prescribeQuantity']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": record.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "nric": nric,
                "clinicId": clinicId,
                "drugName": drugName,
                "date": date,
                "time" : time
            },
            "message": "Patient record not found."
        }
    ), 404


@app.route("/patientRecord/<string:nric>/<string:clinicId>/<string:drugName>/<string:date>/<string:time>", methods=['DELETE'])
def delete_patient_record(nric,clinicId,drugName,date,time):
    record = PatientRecord.query.filter_by(nric=nric,clinicId=clinicId,drugName=drugName,date=date,time=time).first()
    if record:
        db.session.delete(record)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "nric": nric,
                    "clinicId": clinicId,
                    "drugName": drugName,
                    "date": date,
                    "time" : time
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "nric": nric,
                "clinicId": clinicId,
                "drugName": drugName,
                "date": date,
                "time" : time
            },
            "message": "Patient record not found."
        }
    ), 404


if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": patient records ...")
    app.run(host='0.0.0.0', port=5006, debug=True)
