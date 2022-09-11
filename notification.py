# run 'pip install mailjet_rest' for mac run 'python3 -m pip install mailjet_rest'
from mailjet_rest import Client
import json
import sys
import os
from os import environ
import pika

api_key = 'ce935253e850312f41b9c38c450a9ca0'
api_secret = '3fdd8dcf9fd9bb6cf96bb71d97a659ac'
mailjet = Client(auth=(api_key, api_secret), version='v3.1')

hostname = environ.get('rabbit_host') or "localhost" 
port = environ.get('rabbit_port') or 5672 
# connect to the broker and set up a communication channel in the connection
connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
channel = connection.channel()
# set up the exchange if the exchange doesn't exist
exchangename="restock_direct"
channel.exchange_declare(exchange=exchangename, exchange_type='direct', durable=True)

def restock_drug():
    # prepare a queue for receiving messages
    queue_name = "notification"
    channel.queue_declare(queue=queue_name, durable=True)
    channel.queue_bind(exchange=exchangename, queue=queue_name, routing_key='notification.restock')
    channel.basic_qos(prefetch_count=1)
    # set up a consumer and start to wait for coming messages
    channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True) # 'auto_ack=True' acknowledges the reception of a message to the broker automatically, so that the broker can assume the message is received and processed and remove it from the queue
    channel.start_consuming() # an implicit loop waiting to receive messages; it doesn't exit by default. Use Ctrl+C in the command window to terminate it.

def callback(channel, method, properties, body): # required signature for the callback; no return

    result = send_email(json.loads(body))

    json.dump(result, sys.stdout, default=str) # convert the JSON object to a string and print out on screen
    print() # print a new line feed to the previous json dump
    print() # print another new line as a separator


def send_email(message):
    supplierEmail = message['supplierEmail']
    supplierName = message['supplierName']
    drugName = message['drugName']
    reorderQuantity = str(message['reorderQuantity'])
    clinicEmail = message['clinicEmail']
    clinicName = message['clinicName']
    clinicAddress = message['clinicAddress']
    clinicPostalCode = message['clinicPostalCode']
    msg = ''
    data = {
    'Messages': [
        {
        "From": {
            "Email": clinicEmail,
            "Name": clinicName
        },
        "To": [
            {
            "Email": supplierEmail,
            "Name": supplierName
            }
        ],
        "Bcc": [
            {
                "Email": clinicEmail,
                "Name": clinicName
            }
        ],
        "Subject": "Reorder Drug Supplies",
        "TextPart": "Reorder Drugs",
        "HTMLPart": "Dear <b>" + supplierName + "</b>, <br><br> Our branch at <b>"+ clinicName + "</b> has low supplies of <b><u>" + drugName + "</u></b>. We would like to place an order of <b><u>" + reorderQuantity + "</u></b>. Please make the delivery to <b><u>" + clinicAddress + ' (S' + clinicPostalCode + ")</u></b>.<br><br> Thank you for doing business with us! <br><br>Warm Regards, <br>" + clinicName,
        "CustomID": "AppGettingStartedTest"
        }
    ]
    }
    result = mailjet.send.create(data=data)
    print(result.status_code)
    print(result.json())
    return result.json()

if __name__ == "__main__": 
    print("This is " + os.path.basename(__file__) + ": sending an email...")
    restock_drug()