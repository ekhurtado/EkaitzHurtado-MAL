import json
import os, requests
from threading import Thread

from flask import Flask, request

function = os.environ.get('SERVICE')
inPortNumber = os.environ.get('INPORT_NUMBER')

step = os.environ.get('CUSTOM_URRATSA')
multiplier = os.environ.get('CUSTOM_BIDERKATZAILEA')

output = os.environ.get('OUTPUT')
output_port = os.environ.get('OUTPUT_PORT')

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def main():
    print(request)

    # Lehenik eta behin, HTTP mezutik datuak lortuko ditugu
    messageData = None
    if request.method == 'GET':
        # Handle GET requests
        return "GET metodo bat bidali duzu!"
    elif request.method == 'POST':
        # Handle POST requests
        if "text/plain" in request.headers.get("Content-Type"):
            messageData = request.get_data(as_text=True)

    thread_func = None  # Exekuzio-hari berria erabiltzen dugu aurreko osagaiari "OK" mezua lehen baino lehen bidaltzeko
    match function:
        case "BalioaHanditu":
            thread_func = Thread(target=increaseValue, args=(messageData,))
        case "BalioaTxikitu":
            thread_func = Thread(target=decreaseValue, args=(messageData,))
        case "BalioaBiderkatu":
            thread_func = Thread(target=multiplyValue, args=(messageData,))
        case _:
            return "Not function selected"
    # Aukeratu den funtzionalitatea exekuzio-hari berri batean abiarazten dugu
    thread_func.start()
    # Aurreko osagaiari erantzuten diogu dena ondo joan dela esanez
    return "OK\n"


'''
Funtzionalitateak exekutatzeko metodoak
'''


def increaseValue(messageData):
    # HTTP mezuan bidalitako datuetaki balioa lortuko dugu
    jsonData = json.loads(messageData)
    type = jsonData['type']
    value = jsonData['value']

    # Funtzionalitatearen eragiketa betetzen dugu
    value += step

    # Sartutako urratsa mota desberdinekoa izanez, emaitza desberdina izan daiteke, beraz ziurtatuko gara
    match type:
        case "natural" | "integer":
            value = int(value)
        case "float":
            value = float(value)
        case _:
            pass
    # Balio berria edukiz, hurrengo osagaiari pasako diogu
    sendData(type, value)


def decreaseValue(messageData):
    # HTTP mezuan bidalitako datuetaki balioa lortuko dugu
    jsonData = json.loads(messageData)
    type = jsonData['type']
    value = jsonData['value']

    # Funtzionalitatearen eragiketa betetzen dugu
    value -= step

    # Sartutako urratsa mota desberdinekoa izanez, emaitza desberdina izan daiteke, beraz ziurtatuko gara
    match type:
        case "natural" | "integer":
            value = int(value)
        case "float":
            value = float(value)
        case _:
            pass
    # Balio berria edukiz, hurrengo osagaiari pasako diogu
    sendData(type, value)


def multiplyValue(messageData):
    # HTTP mezuan bidalitako datuetaki balioa lortuko dugu
    jsonData = json.loads(messageData)
    type = jsonData['type']
    value = jsonData['value']

    # Sartutako urratsa mota desberdinekoa izanez, emaitza desberdina izan daiteke, beraz ziurtatuko gara
    match type:
        case "natural" | "integer":
            value = value * multiplier  # Funtzionalitatearen eragiketa betetzen dugu
            value = int(value)
        case "float":
            value = value * float(multiplier)  # Funtzionalitatearen eragiketa betetzen dugu
            value = float(value)
        case _:
            pass
    # Balio berria edukiz, hurrengo osagaiari pasako diogu
    sendData(type, value)


def sendData(type, value):
    url = 'http://' + output + ':' + output_port
    headers = {'Content-Type': 'text/plain'}
    try:
        r = requests.post(url, headers=headers, data='{"type": "' + type + '", "value": ' + str(value) + '}')
        print(r.text)
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        print("ERROREA!!! Ezin izan da mezua bidali")
        print(e)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=inPortNumber)
