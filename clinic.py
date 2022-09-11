from tokenize import String
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app)  

class Clinic(db.Model):
    __tablename__ = 'clinic'
    clinicId = db.Column(db.Numeric(3), nullable=False, primary_key=True)
    clinicName = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(128), nullable=False)
    postalCode = db.Column(db.String(6), nullable=False)
    email = db.Column(db.String(128), nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def __init__(self, clinicId, clinicName, address, postalCode, email, password):
        self.clinicId = clinicId
        self.clinicName = clinicName
        self.address = address
        self.postalCode= postalCode
        self.email = email
        self.password = password
    def json(self):
        return {"clinicId": self.clinicId, "clinicName": self.clinicName, "address": self.address, "postalCode": self.postalCode, "email": self.email, "password": self.password}


@app.route("/clinic")
def get_all():
    cliniclist = Clinic.query.all()
    if len(cliniclist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "clinic": [clinic.json() for clinic in cliniclist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no clinics."
        }
    ), 404

#Finding clinics in the district
@app.route("/clinic/postal/<string:patientPostalCode>")
def find_by_patientPostalCode(patientPostalCode):
    district = patientPostalCode[:2]
    clinicsListByDistrict = Clinic.query.filter(Clinic.postalCode.startswith(district)).all()

    if clinicsListByDistrict:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "clinic": [clinic.json() for clinic in clinicsListByDistrict]
                }
            }
        )  
    return jsonify(
        {
            "code": 404, 
            "message": "There are no matching clinics."
        }
    )

@app.route("/clinic/id/<string:clinicId>")
def find_by_clinicId(clinicId):
    clinicId = int(clinicId)
    clinic = Clinic.query.filter_by(clinicId=clinicId).first()
    if clinic:
        return jsonify(
            {
                "code": 200,
                "data": clinic.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Clinic cannot be found."
        }
    ), 404

@app.route("/clinic/<int:clinicId>", methods=['POST'])
def create_clinic(clinicId):
    if (Clinic.query.filter_by(clinicId=clinicId).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "clinicId": clinicId
                },
                "message": "Clinic already exists."
            }
        ), 400

    data = request.get_json()
    clinic = Clinic(clinicId, **data)

    try:
        db.session.add(clinic)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "clinicId": clinicId
                },
                "message": "An error occurred creating the clinic."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": clinic.json()
        }
    ), 201

@app.route("/clinic/<int:clinicId>", methods=['PUT'])
def update_clinic(clinicId):
    clinic = Clinic.query.filter_by(clinicId=clinicId).first()
    if clinic:
        data = request.get_json()
        if data['clinicId']:
            clinic.clinicId = data['clinicId']
        if data['clinicName']:
            clinic.clinicName = data['clinicName'] 
        if data['address']:
            clinic.address = data['address'] 
        if data['postalCode']:
            clinic.postalCode = data['postalCode'] 
        if data['email']:
            clinic.email = data['email']
        if data['password']:
            clinic.password = data['password']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": clinic.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "id": id
            },
            "message": "Clinic not found."
        }
    ), 404


@app.route("/clinic/<int:clinicId>", methods=['DELETE'])
def delete_clinic(clinicId):
    clinic = Clinic.query.filter_by(clinicId=clinicId).first()
    if clinic:
        db.session.delete(clinic)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "clinicId": clinicId
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "clinicId": clinicId
            },
            "message": "Clinic not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)
