from datetime import date, time, datetime, timedelta
from sqlite3 import Date
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS
from sqlalchemy import func 
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app) 

class Appointment(db.Model):
    __tablename__ = 'appointment'
    nric = db.Column(db.String(9), nullable=False, primary_key=True)
    symptoms = db.Column(db.String(128), nullable=False)
    clinicId = db.Column(db.Numeric(3), nullable=False)
    appointmentDate = db.Column(db.String(64), nullable=False, primary_key=True)
    appointmentTime = db.Column(db.String(64), nullable=False, primary_key=True)    

    def __init__(self, nric, symptoms, clinicId, appointmentDate, appointmentTime):
        self.nric = nric
        self.symptoms = symptoms
        self.clinicId = clinicId
        self.appointmentDate = appointmentDate
        self.appointmentTime = appointmentTime
        
        
    def json(self):
        return {"nric": self.nric, "symptoms": self.symptoms, "clinicId": self.clinicId, "appointmentDate": self.appointmentDate, "appointmentTime": self.appointmentTime}

@app.route("/appointment/<string:clinicId>/<string:appointmentDate>")
def get_timeslots(clinicId,appointmentDate): 
    clinicId = int(clinicId)

    appointmentList = Appointment.query.filter_by(clinicId=clinicId, appointmentDate=appointmentDate).all()
    
    if len(appointmentList):
        return jsonify(
            {
                "code": 200,
                "data": {"appts": [appt.json() for appt in appointmentList]}
            }
        )
    return jsonify(
        { 
            "code": 299,
            "message": "No appointments"
        }
    ), 299

@app.route("/createAppointment", methods=["POST"])
def createAppointment():
    data = request.get_json()

    #retrieve the details
    nric = data["nric"]
    symptoms = data["symptoms"]
    clinicId = int(data["clinicId"])
    appointmentDate = data["appointmentDate"]
    appointmentTime = data['appointmentTime']
    
    if (Appointment.query.filter_by(nric=nric,appointmentDate=appointmentDate,appointmentTime=appointmentTime).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "nric": nric,
                    "appointmentDate": appointmentDate,
                    'appointmentTime': appointmentTime
                },
                "message": "Appointment already exists."
            }
        ), 400

    appointment = Appointment(nric, symptoms, clinicId, appointmentDate, appointmentTime)
    
    try:
        db.session.add(appointment)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "message": "Appointment booking failed"
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": appointment.json()
        }
    ), 201

@app.route("/appointment/nric/<string:nric>")
def find_by_nric(nric):
    appointment_list = Appointment.query.filter_by(nric=nric).all()
    if len(appointment_list):
        return jsonify(
            {
                "code": 200,
                "data": [record.json() for record in appointment_list]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Appointment not found."
        }
    ), 404

@app.route("/appointment/date/<string:nric>/<string:appointmentDate>")
def find_by_appointmentDate(nric, appointmentDate):
    appointment_list = Appointment.query.filter_by(nric=nric, appointmentDate=appointmentDate).all()
    if len(appointment_list):
        return jsonify(
            {
                "code": 200,
                "data": [record.json() for record in appointment_list]
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Appointment not found."
        }
    ), 404


@app.route("/appointment/<string:nric>/<string:appointmentDate>/<string:appointmentTime>", methods=['PUT'])
def update_appointment(nric, appointmentDate, appointmentTime):
    appointment = Appointment.query.filter_by(nric=nric, appointmentDate=appointmentDate, appointmentTime=appointmentTime).first()
    if appointment:
        data = request.get_json()
        if data['appointmentTime']:
            appointment.appointmentTime = data['appointmentTime']     
        if data['appointmentDate']:
            appointment.appointmentDate = data['appointmentDate'] 
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": appointment.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "nric": nric,
                "appointmentDate": appointmentDate,
                "appointmentTime": appointmentTime
            },
            "message": "Appointment not found."
        }
    ), 404


@app.route("/appointment/<string:nric>/<string:appointmentDate>/<string:appointmentTime>", methods=['DELETE'])
def delete_appointment(nric,appointmentDate,appointmentTime):
    appointment = Appointment.query.filter_by(nric=nric, appointmentDate=appointmentDate, appointmentTime=appointmentTime).first()
    if appointment:
        db.session.delete(appointment)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "nric": nric,
                    "appointmentDate": appointmentDate,
                    "appointmentTime": appointmentTime
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "nric": nric,
                "appointmentDate": appointmentDate,
                "appointmentTime": appointmentTime
            },
            "message": "appointment not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)
