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

clinic_URL = environ.get('clinic_URL') or "http://localhost:5002/clinic"
distance_URL = environ.get('distance_URL') or "http://localhost:5001/checkDist"
appointment_URL = environ.get('appointment_URL') or "http://localhost:5003/appointment"
patient_URL = environ.get('patient_URL') or "http://localhost:5000/patient/"

@app.route ("/getClinicsName/nric/<string:nric>")
def getClinicsNames(nric):
    all_appt = invoke_http(appointment_URL + "/nric/" + str(nric))
    # print("\n", all_appt)
    code = all_appt["code"]
    if code not in range(200, 300):
        return {
            "code": 404,
            "message": "No appointments made"
        }
    all_appt_result = all_appt["data"]
    for i in range(0,len(all_appt_result)):
        appt = all_appt_result[i]
        clinicId = appt["clinicId"]
        clinic_info = invoke_http(clinic_URL + "/id/" + str(clinicId))
        # print("\n", clinic_info)
        code = clinic_info["code"]
        if code not in range(200, 300):
            return {
                "code": 404,
                "message": "No clinic found"
            }
        clinicName = clinic_info["data"]["clinicName"]
        all_appt_result[i]["clinicName"] = clinicName
    return  {
        "code":200,
        "data": all_appt_result
    }

@app.route("/viewClinics", methods=["POST"])
def viewClinics():
    if request.is_json:
        try:
            patientLocation = request.get_json()
            # print("\n Received an patient location in JSON:", patientLocation)
            listOfClinics = retrieveClinics(patientLocation)
            return listOfClinics

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "viewClinics.py internal error: " + ex_str
            }), 500

    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def retrieveClinics(patientLocation):
    patientPostalCode = patientLocation["postalCode"]

    if patientPostalCode == "":
        patientNRIC = patientLocation["nric"]

        patient_result = invoke_http(patient_URL + str(patientNRIC))
        # print(patient_result)

        code = patient_result["code"]
        if code not in range(200,300):
            return {"code": 404,
            "message": "Patient not logged in"}
        else:
            patientPostalCode= str(patient_result["data"]["postalCode"])

    clinic_result = invoke_http(clinic_URL + "/postal/" + patientPostalCode)
    # print('\n Clinic result:', clinic_result)

    code = clinic_result["code"]
    #no clinic in the region
    if code not in range(200, 300):
        #get all clinics
        clinic_result = invoke_http(clinic_URL)
        #no clinic in database
        if clinic_result["code"] not in range(200,300):
            return {
                "code": 500,
                "message": "No Clinic Nearby! Please use another postal code"
            }
    
    listOfClinics = clinic_result["data"]["clinic"]

    final_clinic = {}
    for i in range(0,len(listOfClinics)):
        clinic = listOfClinics[i]

        final_clinic[clinic["clinicId"]] = {
            "name": clinic["clinicName"], 
            "address": clinic["address"],
            "queue": 0
        }

        #3. Invoke appointmentMS to get queue
        current_date = datetime.datetime.now()
        d1 = datetime.datetime(int(current_date.strftime('%Y')), int(current_date.strftime('%m')), int(current_date.strftime('%d')), int(current_date.strftime('%H')),int(current_date.strftime('%M')),int(current_date.strftime('%S')))
        
        if current_date.strftime('%m')[0] == "0":
            today_month = current_date.strftime('%m')[1]
        else:
            today_month = current_date.strftime('%m')
        if current_date.strftime('%d')[0] == "0":
            today_day = current_date.strftime('%d')[1]
        else: 
            today_day = current_date.strftime('%d')
        
        today_date = current_date.strftime("%Y")+"-"+today_month+'-'+today_day
        
        appointment_list = invoke_http(appointment_URL + '/' + str(clinic["clinicId"]) + '/' + today_date, method='GET')
        
        code = appointment_list['code']
        if code not in range(200, 300):
            return {
                "code": 404,
                "message": "Failed to retrieve appointments",
                "data": {
                    "clinicId": str(clinic["clinicId"]),
                    "appointmentDate": today_date
                }
            }
        appt_timings = []
        if code == 299:
            pass
        else:
            for appt in appointment_list["data"]["appts"]:
                appt_timings.append(appt['appointmentTime'])
                
        if int(current_date.strftime('%M')) > 30:
            time_to_check = str(int(current_date.strftime('%H')) + 1) + ":00:00"
        else:
            time_to_check = current_date.strftime('%H') + ":30:00"

        check_time_now = int("".join(time_to_check.split(":")))
        if check_time_now in range(0,90000):
            time_to_check = "09:00:00"

        if time_to_check not in appt_timings:
            final_clinic[clinic["clinicId"]]["queue"] = 0
        else:
            timeslot_list = ["09:00:00","09:30:00","10:00:00","10:30:00","11:00:00","11:30:00","12:00:00","12:30:00","13:00:00","13:30:00","14:00:00","14:30:00","15:00:00","15:30:00","16:00:00","16:30:00"]
            queue_count = 0
            for time in timeslot_list:
                if check_time_now <= int("".join(time.split(":"))):
                    if time in appt_timings:
                        queue_count += 1
                    else:
                        break
            final_clinic[clinic["clinicId"]]["queue"] = queue_count
        
    #create object to send to distanceMS
    check_distance = { 
        "patientAddress": patientPostalCode,
        "clinics": [clinic["postalCode"] for clinic in listOfClinics]
    }
    
    #4. Invoke distance microservice
    distance_result = invoke_http(distance_URL, method="POST", json=check_distance)
    # print("\n Distance result:", distance_result)

    code = distance_result["code"]
    #location found
    if code in range(200, 300):
        distance_compare = distance_result["data"]["rows"][0]["elements"]

        #append distance
        for i in range(0,len(listOfClinics)):
            final_clinic[listOfClinics[i]["clinicId"]]["distance"] = distance_compare[i]["distance"]["value"]

        #sort by distance
        final_clinic = sorted(final_clinic.items(), key= lambda x: x[1]["distance"])
    
    else:
        final_clinic = sorted(final_clinic.items())

    return {
        "code":200,
        "data": final_clinic
    }

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5100, debug=True)