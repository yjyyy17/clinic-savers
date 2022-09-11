from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ
import pika
import requests
import json
from invokes import invoke_http

app = Flask(__name__)
CORS(app)

patientRecord_URL = environ.get('patientRecord_URL') or "http://localhost:5006/patientRecord/"
drug_URL = environ.get('drug_URL') or "http://localhost:5007/drug/"
clinic_URL = environ.get('clinic_URL') or "http://localhost:5002/clinic/"

@app.route("/create_record", methods=['POST'])
def create_record():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            patientRecord = request.get_json()
            print("\nReceived an patient record in JSON:", patientRecord)

            # do the actual work
            # Send patient record info
            result = processPatientRecordAdd(patientRecord)
            return result

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            # print(ex_str)

            return jsonify({
                "code": 500,
                "message": "prescribeDrug.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400


def processPatientRecordAdd(patientRecord):
    # Send the patient record info
    # Invoke the patientRecord microservice
    print('\n-----Invoking patientRecord microservice-----')
    patient_nric_str = patientRecord['nric']
    del patientRecord['nric']
    record_result = invoke_http(patientRecord_URL + patient_nric_str , method='POST', json=patientRecord)
    # print('record_result:', record_result)


    # Check the creating patient record result failure
    code = record_result["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"record_result": record_result},
            "message": "Patient record creation failure."
        }
    # Retrieve drug information
    # Invoke the drug microservice
    print('\n-----Invoking drug microservice-----')
    patient_drug_qty = patientRecord['prescribeQuantity']
    patient_drugName = patientRecord['drugName']
    patient_clinicId = str(patientRecord['clinicId'])
    drug = invoke_http(drug_URL + patient_clinicId + '/' + patient_drugName , method='GET')
    code = drug["code"]
    
    # Check if retrieve drug information failure
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"drug": drug},
            "message": "Retrieve Drug Record failure."
        }

    # Update drug quantity
    # Invoke the drug microservice
    print('\n-----Invoking drug microservice-----')
    drug_qty = drug["data"]['quantity']
    new_qty = drug_qty - patient_drug_qty
    drug_result = invoke_http(drug_URL + patient_clinicId + '/' + patient_drugName, method='PUT', json={"quantity": new_qty})
    # print(drug_result)

    # Check if drug update failure
    code = drug_result["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"drug_result": drug_result},
            "message": "Drug record update failure."
        }
    # Check if updated quantity falls below safety stock levels
    if new_qty < 100 and drug_result["data"]["restockStatus"] == "no":
        # create message to send via AMQP
        message = createNotificationMessage(drug_result["data"])
        # send message to the exchange
        send_restock(message)
        # Update drug restockStatus
        # Invoke the drug microservice
        print('\n-----Invoking drug microservice-----')
        new_drug_result = invoke_http(drug_URL + patient_clinicId + '/' + patient_drugName, method='PUT', json={"restockStatus": "yes"})
        # check if drug update failure
        code = new_drug_result["code"]
        if code not in range(200, 300):
            # Return error
            return {
                "code": 500,
                "data": {"new_drug_result": new_drug_result},
                "message": "Update Drug Record failure."
            }
        # Successfully sent email to supplier
        return {
            "code": 202,
            "message": "Successfully restocked! Email send to supplier! Patient Record Created Successfully!",
            "data": {
                "record_result": record_result,
                "drug_result": drug_result,
                "new_drug_result": new_drug_result,
                "message": message
            }
        }
        
    # Return patientRecord, drug information
    return {
        "code": 201,
        "data": {
            "record_result": record_result,
            "drug_result": drug_result
        }
    }
@app.route("/delete_record", methods=['POST'])
def delete_record():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            patientRecord = request.get_json()
            print("\nReceived an patient record in JSON:", patientRecord)

            # do the actual work
            # Send patientRecord information to delete
            result = processPatientRecordDelete(patientRecord)
            return result

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            # print(ex_str)

            return jsonify({
                "code": 500,
                "message": "prescribeDrug.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processPatientRecordDelete(patientRecord):
    #  Retrieve patientRecord information
    # Invoke the patientRecord microservice
    print('\n-----Invoking patientRecord microservice-----')
    patient_nric_str = patientRecord['nric']
    patient_clinic_str = str(patientRecord['clinicId'])
    patient_drug_str = patientRecord['drugName']
    patient_date_str = patientRecord['date']
    patient_time_str = patientRecord['time']
    # print(patientRecord)
    record_result = invoke_http(patientRecord_URL + patient_nric_str + '/' + patient_clinic_str + '/' + patient_drug_str + '/' + patient_date_str + '/' + patient_time_str, method='DELETE')
    # print('record_result:', record_result)


    # Check if retrieve patientRecord failure
    code = record_result["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"record_result": record_result},
            "message": "Patient record delete failure."
        }
    
    #  Retrieve specific drug information
    # Invoke the drug microservice    
    print('\n-----Invoking drug microservice-----')
    patient_drug_qty = patientRecord['prescribeQuantity']
    drug = invoke_http(drug_URL + patient_clinic_str + '/' + patient_drug_str, method='GET')

    #check if retrieve drug information error
    code = drug["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"drug": drug},
            "message": "Retrieve Drug Record failure."
        }
    #  Update specific drug 
    # Invoke the drug microservice    
    print('\n-----Invoking drug microservice-----')
    drug_qty = drug["data"]['quantity']
    new_qty = drug_qty + patient_drug_qty
    drug_result = invoke_http(drug_URL + patient_clinic_str + '/' + patient_drug_str, method='PUT', json={"quantity": new_qty})

    #check if update drug error
    code = drug_result["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"drug_result": drug_result},
            "message": "Drug record update failure."
        }
        
    #  Return deleted patientRecord, drug information
    return {
        "code": 201,
        "data": {
            "record_result": record_result,
            "drug_result": drug_result
        }
    }
@app.route("/update_record", methods=['POST'])
def update_record():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            patientRecord = request.get_json()
            print("\nReceived an patient record in JSON:", patientRecord)

            # do the actual work
            # Send order info {cart items}
            result = processPatientRecordUpdate(patientRecord)
            return result

        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            # print(ex_str)

            return jsonify({
                "code": 500,
                "message": "prescribeDrug.py internal error: " + ex_str
            }), 500

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processPatientRecordUpdate(patientRecord):
    # Retrieve patientRecord information
    # Invoke the patientRecord microservice
    print('\n-----Invoking patientRecord microservice-----')
    patient_nric_str = patientRecord['nric']
    patient_clinic_str = str(patientRecord['clinicId'])
    patient_drug_str = patientRecord['drugName']
    patient_date_str = patientRecord['date']
    patient_time_str = patientRecord['time']
    record_result = invoke_http(patientRecord_URL + patient_nric_str + '/' + patient_clinic_str + '/' + patient_drug_str + '/' + patient_date_str + '/' + patient_time_str, method='GET')

    # Check if retrieve patientRecord error
    code = record_result["code"]
    if code not in range(200, 300):
        # 7. Return error
        return {
            "code": 500,
            "data": {"record_result": record_result},
            "message": "Patient record search failure."
        }

    # print('record_result:', record_result)

    # Update patientRecord information
    # Invoke the patientRecord microservice
    print('\n-----Invoking patientRecord microservice-----')
    del patientRecord['nric']
    del patientRecord['clinicId']
    del patientRecord['drugName']
    del patientRecord['date']
    del patientRecord['time']
    new_record_result = invoke_http(patientRecord_URL + patient_nric_str + '/' + patient_clinic_str + '/' + patient_drug_str + '/' + patient_date_str + '/' + patient_time_str, method='PUT',json=patientRecord)

    # check if Update patientRecord information error
    code = new_record_result["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"new_record_result": new_record_result},
            "message": "Patient record update failure."
        }
    # Retrieve specific drug information
    # Invoke the drug microservice
    print('\n-----Invoking drug microservice-----')
    patient_drug_qty = record_result['data']['prescribeQuantity']
    new_patient_drug_qty = new_record_result['data']['prescribeQuantity']
    drug = invoke_http(drug_URL + patient_clinic_str + '/' + patient_drug_str, method='GET')
    # check if retrieve drug error
    code = drug["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"drug": drug},
            "message": "Retrieve Drug Record failure."
        }

    # Update specific drug information
    # Invoke the drug microservice
    print('\n-----Invoking drug microservice-----')
    drug_qty = drug["data"]['quantity']
    new_qty = drug_qty + patient_drug_qty - new_patient_drug_qty
    drug_result = invoke_http(drug_URL + patient_clinic_str + '/' + patient_drug_str, method='PUT', json={"quantity": new_qty})

    # Check if update drug error
    code = drug_result["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"drug_result": drug_result},
            "message": "Drug record update failure."
        }
    
    # Check if updated quantity falls below safety stock levels
    if new_qty < 100 and drug_result["data"]["restockStatus"] == "no":
        # create message to send via AMQP
        message = createNotificationMessage(drug_result["data"])
        # send message to the exchange
        send_restock(message)
        # Update drug restockStatus
        # Invoke the drug microservice
        print('\n-----Invoking drug microservice-----')
        new_drug_result = invoke_http(drug_URL + patient_clinic_str + '/' + patient_drug_str, method='PUT', json={"restockStatus": "yes"})
        # check if update drug error
        code = new_drug_result["code"]
        if code not in range(200, 300):
            # Return error
            return {
                "code": 500,
                "data": {"new_drug_result": new_drug_result},
                "message": "Update Drug Record failure."
            }
        # Successfully sent email to supplier
        return {
            "code": 202,
            "message": "Successfully restocked! Email send to supplier! Patient Record Updated Successfully!",
            "data": {
                "record_result": record_result,
                "drug_result": drug_result,
                "new_drug_result": new_drug_result,
                "message": message
            }
        }
        
    # 7. Return updated patientRecord, drug information
    return {
        "code": 201,
        "data": {
            "record_result": record_result,
            "drug_result": drug_result
        }
    }

def createNotificationMessage(drug_record):
    print('\n-----Invoking clinic microservice-----')
    clinicId = str(drug_record['clinicId'])
    clinic_record = invoke_http(clinic_URL + 'id/' + clinicId, method='GET')
    clinicName = clinic_record['data']['clinicName']
    clinicAddress = clinic_record['data']['address']
    clinicPostalCode = clinic_record['data']['postalCode']
    clinicEmail = clinic_record['data']['email']

    # Check the clinic result if error;
    code = clinic_record["code"]
    if code not in range(200, 300):
        # Return error
        return {
            "code": 500,
            "data": {"record_result": clinic_record},
            "message": "Clinic record search failure."
        }
    supplierName = drug_record['supplierName']
    supplierEmail = drug_record['supplierEmail']
    reorderQuantity = drug_record['reorderQuantity']
    drugName = drug_record['drugName']
    message = {"supplierName":supplierName,"supplierEmail":supplierEmail,"reorderQuantity":reorderQuantity,"drugName":drugName,"clinicName":clinicName,"clinicAddress":clinicAddress,"clinicPostalCode":clinicPostalCode,"clinicEmail":clinicEmail}
    return message

# send Restock to Notification through AMQP
def send_restock(message):
    """send supplier, clinic, drug information to Notification """
    hostname = environ.get('rabbit_host') or "localhost"
    port = environ.get('rabbit_port') or 5672
    # connect to the broker and set up a communication channel in the connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
    channel = connection.channel()
 
    # set up the exchange if the exchange doesn't exist
    exchangename="restock_direct"
    channel.exchange_declare(exchange=exchangename, exchange_type='direct', durable=True)

    # prepare the message body content
    message = json.dumps(message, default=str) # convert a JSON object to a string

    # send message to Notifications
    # prepare the channel and send a message to Notifications
    channel.queue_declare(queue='notification', durable=True)
    # make sure the queue is bound to the exchange
    channel.queue_bind(exchange=exchangename, queue='notification', routing_key='notification.restock')
    channel.basic_publish(exchange=exchangename, routing_key="notification.restock", body=message,
        properties=pika.BasicProperties(delivery_mode = 2, 
        )
    )
    # close the connection to the broker
    connection.close()
    


# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for prescribing a drug...")
    app.run(host="0.0.0.0", port=5120, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
