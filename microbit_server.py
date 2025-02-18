#  Programme développer par Anthony PENHARD pour piloter des maquettes en classe de technologie Collège Ac-Rennes
#
# V1_0_0 : initiale prend le dernier pour COM pour afficher valeures reçu et possible envoi manuellement datas
# V1_0_1 : ajout page Config et amélioration de index avec 20 cartes affichées
# V1_0_2 : ajout page RFID avec 09 ilôts
# V1_0_3 : ajout fichier de config.ini + pas mal de templates ...
# V2_0_0 : ajout fichier du websocket au lieu d'un pooling toutes les 1s, j'ai gardé la section api pour envoyer à la MB
# V2_0_1 : si fichier config.ini absent, défini par défaut une config
# V2_0_2 : ajout a config.ini les données pour le parking trottinette
# V2_0_3 : réfelxion sur le nom et dépot sur un github : Ma

import serial
import serial.tools.list_ports
import time
#import csv
from datetime import datetime
from flask import Flask, jsonify, render_template, request
from configparser import ConfigParser
from flask_socketio import SocketIO
from engineio.async_drivers import threading
import threading
#import numpy as np

# Variable globale pour stocker les dernières données reçues
#latest_data = {"valeur": None, "num_carte": None}
latest_data = {"valeur": None}

# Initialisation de Flask et Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# fichier de configuration ini
# https://docs.python.org/fr/3/library/configparser.html

config = ConfigParser() 
try:
    with open('config.ini') as f:
        config.read('config.ini')
        config_settings = config['settings']
        if not config['Parking']:
            config['Parking'] = {'Data_format': 'Parking', 'Nb_Parking': '16', 'Liste_Parking': 'letter'}
except IOError:
    print("le fichier config.ini n'est pas présent.")
    config_settings = {'serial_port': 'COM4', 'cnx_auto': 'On', 'baud_rate': '115200', 'groupe_radio': '99'}
    config['settings'] = config_settings
    config['Parking'] = {'Data_format': 'Parking', 'Nb_Parking': '16', 'Liste_Parking': 'letter'}

#print(vars(config))

# Configuration du port série
SERIAL_PORT = config_settings.get('serial_port', 'COM4')
BAUD_RATE = int(config_settings.get('baud_rate', '115200'))

# groupe_radio utilisé par la carte micro:Bit
groupe_radio = int(config_settings.get('groupe_radio', '99'))

# connexion automatique On/Off
cnx_auto = bool(config_settings.get('cnx_auto', True))

#/fin fichier de configuration ini

# affiche la liste des ports disponibles
serial_ports = serial.tools.list_ports.comports()
for port in serial_ports:
    SERIAL_PORT = port.device
    print(f"{port.name} // {port.device} // D={port.description}")
print(len(serial_ports), ' ports COM trouvés on prend le dernier')

time.sleep(1)
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
time.sleep(1)
# Fonction pour envoyer une commande au Micro:bit
def send_to_microbit(value):
    global ser
    try:
        ser.write(f"{value}\n".encode())  # Envoi de la command avec un saut de ligne
        print(f"Envoyé au Micro:bit : {value}")
    except Exception as e:  
        print(f"Erreur d'envoi série : {e}")

# Fonction pour lire le port série en continu
def read_serial():
    global latest_data
    global ser
    while True:
        data = ser.readline().decode().strip()
        if data:
            print(f"Donnée reçue : {data}")
            latest_data["valeur"] = data
            # Envoyer les données en temps réel à la page Web via WebSocket
            socketio.emit('update_data', latest_data)
        time.sleep(0.1)

# Fonction pour lire le port série en continu
t = threading.Thread(target=read_serial, daemon=True)
def thread_serie():
    global t
    # Démarrer la lecture série dans un thread séparé
    t.etat = True
    t.start()

# si cnx_auto est a On/True dans le fichier de config.ini alors on lance le thread tout de suite
if cnx_auto :
    t.etat = True
    t.start()

# WebSocket pour recevoir les commandes depuis la page Web
@socketio.on('send_command')
def handle_command(command):
    print(f"Commande reçue depuis WebSocket : {command}")
    send_to_microbit(command)

# WebSocket
@app.route('/socket')
def socket():
    return render_template("socket.html")

# Route API pour obtenir la dernière valeur
@app.route('/api/data', methods=['GET'])
def get_data():
    global latest_data
    return jsonify(latest_data)

# Route API pour envoyer une commande au Micro:bit
@app.route('/api/send', methods=['POST'])
def send_command():
    value = request.json.get("value")
    if value is not None:
        send_to_microbit(value)
        return jsonify({"status": "Envoyé", "value": value})
    return jsonify({"status": "Erreur", "message": "Valeur non valide"}), 400

# Route pour servir l'interface Web
@app.route('/index')
@app.route('/')
def index():
    return render_template("index.html")

@app.route('/config')
def config_interface():
    return render_template("config.html", serial_ports=serial_ports , nb_port_COM=len(serial_ports) , BAUD_RATE=BAUD_RATE , cnx_auto=cnx_auto , groupe_radio=groupe_radio, config=config )

# Route API config générale "settings"
@app.route('/api/config', methods=['POST'])
def send_config():
    SERIAL_PORT = request.json.get("serial_port")
    BAUD_RATE = request.json.get("BAUD_RATE")
    cnx_auto = request.json.get("cnx_auto")
    groupe_radio = request.json.get("groupe_radio")
    print(f"Donnée config settings : {SERIAL_PORT} // {BAUD_RATE} // {cnx_auto} // {groupe_radio}")
    return jsonify({"status": "Envoyé", "serial_port": SERIAL_PORT , "BAUD_RATE": BAUD_RATE , "cnx_auto": cnx_auto , "groupe_radio": groupe_radio })

# Route API config "Parking"
@app.route('/api/configParking', methods=['POST'])
def send_configParking():
    #config['Parking'] = {'Data_format': 'Parking', 'Nb_Parking': '16', 'Liste_Parking': 'letter'}
    config['Parking']['Data_format'] = request.json.get("Data_format")
    config['Parking']['Liste_Parking'] = request.json.get("Liste_Parking")
    config['Parking']['Nb_Parking'] = request.json.get("Nb_Parking")
    #print(f"Donnée config Parking : {Data_format} // {Liste_Parking} // {Nb_Parking} ")
    print(f"Donnée config Parking : {config['Parking']['Data_format']} // {config['Parking']['Liste_Parking']} // {config['Parking']['Nb_Parking']} ")
    #print(vars(config['Parking']))
    return jsonify({"status": "Envoyé", "Data_format": config['Parking']['Data_format'] , "Liste_Parking": config['Parking']['Liste_Parking'] , "Nb_Parking": config['Parking']['Nb_Parking'] })

# Route API start le thread de la connexion série de la carte Micro:Bit
@app.route('/api/thread')
def start_thread():
    thread_serie()
    return "Thread Cnx Série Micro:Bit lancé"

@app.route('/api/threadstop')
def stop_thread():
    global t
    # Stoppe le thread de lecture série 
    t.etat = False
    t.stop()
    return "Thread Cnx Série Micro:Bit STOP"

@app.route('/version')
def version():
    return "Fait par Anthony PENHARD Prof Technologie Ac-Rennes V2.0.3"

# Route pour servir l'interface Web rfid
@app.route('/rfid')
def rfid():
    return render_template("rfid.html")

# Route pour servir l'interface Web lapin Karotz / Nabaztag
@app.route('/lapin')
def lapin():
    return render_template("lapin.html", groupe_radio = groupe_radio)

# Route pour servir l'interface Web Parkings Trotinettes
@app.route('/trott')
def trott():
    Data_format = str(config['Parking'].get('Data_format', 'Parking'))
    Nb_Parking = int(config['Parking'].get('Nb_Parking', '16'))
    if config['Parking'].get('Liste_Parking') == 'number' :
        Liste_Parking = ['01', '02', '03', '04', '05', '06', '07', '08', '09', 10, 11, 12, 13, 14, 15, 16]
    else:
        Liste_Parking = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    #elif config['Parking'].get('Liste_Parking') == 'letter' :
    #    Liste_Parking = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
    #else:  # ici config perso / compliqué a gérer a mon sens mélange de lettre et nombre parait peu logique !!
    #    Liste_Parking = config['Parking'].get('Liste_Parking')
    return render_template("trott.html", Data_format = Data_format, Nb_Parking = Nb_Parking, Liste_Parking = Liste_Parking, Conf_liste = config['Parking'].get('Liste_Parking'))

# Route pour servir l'interface Web Afichage data de 20 cartes 
@app.route('/cartes')
def cartes():
    return render_template("cartes.html", groupe_radio = groupe_radio)

# Route pour servir l'interface Web charts génère un graphique
@app.route('/charts')
def charts():
    return render_template("charts.html")

# Route pour servir l'interface Web charts génère un graphique
@app.route('/charts_multi')
def charts_multi():
    return render_template("charts_multi.html")

# Lancement du serveur Flask
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
