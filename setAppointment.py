from operator import itemgetter
from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

import datetime

import json

app = Flask(__name__)
CORS(app)

appt_URL = environ.get('appt_URL') or "http://localhost:5003/createAppointment"
subsidy_URL = environ.get('subsidy_URL') or "http://localhost:5004/subsidy/"

@app.route("/set_appointment", methods=['POST'])
def check_appointment():
    if request.is_json:
        try:
            appt_details = request.get_json()
            # print("\n Appointment info in JSON:", appt_details)
            appt_result = set_appointment(appt_details)
            return appt_result
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)
            return jsonify({
                "code": 500,
                "message": "setAppointment.py internal error: " + ex_str
            }), 500

    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def set_appointment(appt_details):
    appt_result = invoke_http(appt_URL, method="POST", json=appt_details)
    # print("\n Appointment result", appt_result)

    code = appt_result["code"]
    if code not in range(200, 300):
        return {
            "code": 500,
            "data": appt_result,
            "message": "Appointment has already been created"
        }

    else:
        nric = appt_details["nric"]
        subsidy_result = invoke_http(subsidy_URL + str(nric))
        # print("\n Subsidy result:", subsidy_result)
        code = subsidy_result["code"]
        if code not in range(200,300):
            return {
                "code": 255,
                "message": "Appointment successfully created. No subsidy card available!"
            }
        else:
            current_date = datetime.datetime.now().date()
            d1 = datetime.datetime(int(current_date.strftime('%Y')), int(current_date.strftime('%m')), int(current_date.strftime('%d')))
            d2 = datetime.datetime(int(subsidy_result["data"]["expiryDate"].split('-')[0]), int(subsidy_result["data"]["expiryDate"].split('-')[1]), int(subsidy_result["data"]["expiryDate"].split('-')[2]))
            #card expired
            if d2 < d1:
                subsidy_delete = invoke_http(subsidy_URL + str(subsidy_result["data"]['cardNumber']), method="DELETE")
                #return with a unique code number which means expired then in js check that num then alert
                code = subsidy_delete['code']
                if code not in range(200,300):
                    return jsonify({
                        "code": 400,
                        "data" : {"subsidy_card":subsidy_delete},
                        "message": "Error in deleting subsidy card!"
                    }), 400
                return {
                    "code": 256,
                    "data": {"subsidy_card": subsidy_delete["data"]["subsidy"]},
                    "message": "Appointment successfully created. Your " + subsidy_result["data"]["cardType"] + " card has expired. It has been deleted in your subsidy wallet."
                }
            #card not expired
            return {
                "code": 257,
                "message": "Appointment successfully created. Your "+  subsidy_result["data"]["cardType"] +" card is still in use!"
            }
            

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for placing an order...")
    app.run(host="0.0.0.0", port=5008, debug=True)