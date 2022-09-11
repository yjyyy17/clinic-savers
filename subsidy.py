from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import date, datetime
from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app) 

class Subsidy(db.Model):
    __tablename__ = 'subsidy'
    cardNumber = db.Column(db.String(64), nullable=False, primary_key=True)
    nric = db.Column(db.String(9), nullable=False)
    cardType = db.Column(db.String(128), nullable=False)
    organisationType = db.Column(db.String(128), nullable=True)
    expiryDate = db.Column(db.String(64), nullable=False)

    def __init__(self, cardNumber, nric, cardType, organisationType, expiryDate):
        self.cardNumber = cardNumber
        self.nric = nric
        self.cardType = cardType
        self.organisationType = organisationType
        self.expiryDate = expiryDate
        
    def json(self):
        return {"cardNumber": self.cardNumber, "nric": self.nric, "cardType": self.cardType, "organisationType": self.organisationType, "expiryDate": self.expiryDate,}

@app.route("/subsidy/<string:nric>")
def find_by_nric(nric):
    subsidy = Subsidy.query.filter_by(nric=nric).first()

    if subsidy:
        return jsonify(
            {
                "code": 200,
                "data": subsidy.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No subsidy card."
        }
    ), 404

@app.route("/subsidy/<string:cardNumber>", methods=['POST'])
def create_subsidyCard(cardNumber):
    if (Subsidy.query.filter_by(cardNumber=cardNumber).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "cardNumber": cardNumber
                },
                "message": "Subsidy card already exists."
            }
        ), 400

    data = request.get_json()
    subsidy = Subsidy(cardNumber, **data)

    try:
        db.session.add(subsidy)
        db.session.commit()
    except:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "cardNumber": cardNumber
                },
                "message": "An error occurred creating the subsidy card."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": subsidy.json()
        }
    ), 201

@app.route("/subsidy/<string:cardNumber>", methods=['PUT'])
def update_subsidy(cardNumber):
    subsidy = Subsidy.query.filter_by(cardNumber=cardNumber).first()
    if subsidy:
        data = request.get_json()
        if data['nric']:
            subsidy.nric = data['nric']
        if data['cardType']:
            subsidy.cardType = data['cardType'] 
        if data['organisationType']:
            subsidy.organisationType = data['organisationType']     
        if data['expiryDate']:
            subsidy.expiryDate = data['expiryDate'] 

        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": subsidy.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "cardNumber": cardNumber
            },
            "message": "Card not found."
        }
    ), 404


@app.route("/subsidy/<string:cardNumber>", methods=['DELETE'])
def delete_subsidy(cardNumber):
    subsidy = Subsidy.query.filter_by(cardNumber=cardNumber).first()
    if subsidy:
        db.session.delete(subsidy)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "subsidy": subsidy.json()
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "subsidy": subsidy.json()
            },
            "message": "Card not found."
        }
    ), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True)