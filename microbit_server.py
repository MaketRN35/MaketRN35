#  Programme développer par Anthony PENHARD pour piloter des maquettes en classe de technologie Collège Ac-Rennes
#
# Cf. Changelog.md

import serial
import serial.tools.list_ports
import time
import os
import sys
from datetime import datetime
from flask import Flask, jsonify, render_template, render_template_string, request, send_from_directory, abort
from configparser import ConfigParser
from flask_socketio import SocketIO
from engineio.async_drivers import threading
import threading

# Variable globale pour stocker les dernières données reçues
latest_data = {"valeur": None}

# Initialisation de Flask et Flask-SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="threading")

# fichier de configuration ini
config = ConfigParser() 
try:
    with open('config.ini', 'r', encoding='utf-8') as f:
        config.read('config.ini', 'UTF-8')
        config_settings = config['settings']
        # Configuration du port série
        SERIAL_PORT = config_settings.get('serial_port', 'COM4')
        BAUD_RATE = int(config_settings.get('baud_rate', '115200'))

        # groupe_radio utilisé par la carte micro:Bit
        groupe_radio = int(config_settings.get('groupe_radio', '99'))

        # connexion automatique On/Off
        cnx_auto = config_settings.getboolean('cnx_auto', True)
        mode_namevalue = config_settings.get('mode_namevalue', 0)
except IOError:
    print("Fichier config.ini non présent.")
    # Configuration du port série
    SERIAL_PORT = 'COM4'
    BAUD_RATE = 115200
    groupe_radio = 99
    cnx_auto = True
    mode_namevalue = 0

#/fin fichier de configuration ini

# Obtenir le chemin du répertoire où l'exécutable est lancé
if getattr(sys, 'frozen', False):
    # Le script est exécuté en tant qu'exécutable
    root_dir = sys._MEIPASS
else:
    # Le script est exécuté normalement
    root_dir = os.path.dirname(os.path.abspath(__file__))

# affiche la liste des ports disponibles
print("Ports COM trouvés : ( on prend le dernier )")
serial_ports = serial.tools.list_ports.comports()
for port in serial_ports:
    SERIAL_PORT = port.device
    print(f"{port.name} // {port.device} // D={port.description}")

time.sleep(1)
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print("Connexion au port série réussie ")
except Exception as e:
    print(f"Erreur connexion port série : {e}")
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
    global groupe_radio
    # Démarrer la lecture série dans un thread séparé
    t.etat = True
    t.start()
    # dès le démarrage envoi le groupe_radio qui a pu être modifié dans le fichier config
    send_to_microbit('groupe_radio:' + str(groupe_radio))
    #TODO a tester send_to_microbit('mode_namevalue:' + int(mode_namevalue))

# si cnx_auto est a On/True dans le fichier de config.ini alors on lance le thread tout de suite
if cnx_auto :
    t.etat = True
    t.start()
    # dès le démarrage envoi le groupe_radio qui a pu être modifier dans le fichier config
    send_to_microbit('groupe_radio:' + str(groupe_radio))
    #TODO a tester send_to_microbit('mode_namevalue:' + int(mode_namevalue))

# WebSocket pour recevoir les commandes depuis la page Web
@socketio.on('send_command')
def handle_command(command):
    print(f"Commande reçue depuis WebSocket : {command}")
    send_to_microbit(command)

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
    # TODO a modifier car ne fonctionne pas ...
    t.stop()
    return "Thread Cnx Série Micro:Bit STOP"

# Route pour servir l'interface Web
@app.route('/index')
@app.route('/')
def index():
    return render_template("index.html", config=config )

@app.route('/config')
def config_interface():
    return render_template("config.html", serial_ports=serial_ports , nb_port_COM=len(serial_ports) , 
        BAUD_RATE=BAUD_RATE , cnx_auto=cnx_auto , mode_namevalue=mode_namevalue, groupe_radio=groupe_radio, config=config )

# Route API config générale "settings"
@app.route('/api/config', methods=['POST'])
def send_config():
    global ser
    SERIAL_PORT = request.json.get("serial_port")
    BAUD_RATE = request.json.get("BAUD_RATE")
    cnx_auto = request.json.get("cnx_auto")
    mode_namevalue = request.json.get("mode_namevalue")
    groupe_radio = request.json.get("groupe_radio")
    print(f"Donnée config settings : {SERIAL_PORT} // {BAUD_RATE} // {cnx_auto} // {mode_namevalue} // {groupe_radio}")
    time.sleep(1)
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        print("Connexion au port série réussie ")
    except Exception as e:
        print(f"Erreur connexion port série : {e}")
    time.sleep(1)
    return jsonify({"status": "Envoyé", "serial_port": SERIAL_PORT , "BAUD_RATE": BAUD_RATE , "cnx_auto": cnx_auto , "mode_namevalue":mode_namevalue , "groupe_radio": groupe_radio })

@app.route('/about')
@app.route('/version')
def version():
    return "Fait par Anthony PENHARD Prof Technologie Ac-Rennes V2.1.0"

# utiliser un template externe qui est à la racine de l'executable et non intégré <fichier>.html
template_externe = False
@app.route('/external/<fichier>')
def external_template(fichier):
    global template_externe
    print(f"Appel de la fonction external !! {template_externe}")
    template_externe = True
    return default(fichier)

def template_exists(template_name):
    # Construire le chemin complet vers le fichier template
    template_path = os.path.join(root_dir, 'templates', template_name)
    # Vérifier si le fichier existe
    return os.path.exists(template_path)

# "TODO à tester" pour pouvoir utiliser des images externes :
# utiliser des images qui sont externes à l'executable et positionnées à la racine de l'executable
# il est possible de gérer le path directement ici plutôt que dans les templates :
# static_file_url = url_for('static', filename='internal_file.png')
# external_file_url = url_for('serve_external', filename='external_image.png')
@app.route('/imgexternal/<path:filename>')
def serve_external(filename):
    # Servez les fichiers externes depuis le répertoire racine
    return send_from_directory(root_dir, filename)
    # dans le template utiliser : 'serve_external' au lieu de 'static' et donc interne à l'executable
    # <img src="{{ url_for('serve_external', filename=external_image) }}" alt="External Image">

# /fin "TODO à tester"

# Route pour servir l'interface Web Potager Connecté
@app.route("/<name>")
def default(name):
    global template_externe
    print(f"Appel template {name} ") #  {template_externe}
    if template_externe:
        print(f" EXTERNE via http://localhost:5000/external/{name}")
    else:
        print(f" INTERNE via http://localhost:5000/{name}")
    if name in config:
        # si existe section [name] dans config.ini on affiche tous les key : value
        print(f" Config : {config[name]}")
        #print(vars(config[name]))
        for key, value in config.items(name):
            print(f"{key} : {value}")

    # la section [name] n'existe pas dans le fichier config 
    if name not in config:
        print(f" pas de section [{name}] dans le fichier config.ini ")
        config[name] = {}
    Titre = str(config[name].get('titre', 'Maquettes pour ' + name ))
    Sous_titre  = str(config[name].get('sous_titre', ''))
    Data_format = str(config[name].get('data_format', name))
    Valeur_defaut = config[name].get('valeur_defaut', '0123456789')
    # si pas de 'Liste_Maquettes' dans la section du config.ini
    if 'liste_maquettes' not in config[name]:
        config[name]['liste_maquettes'] = '01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20'
    Liste_Maquettes = [e.strip() for e in config[name].get('liste_maquettes').split(',')]
    Nb_Maquettes = int(config[name].get('nb_maquettes', '16'))
    Img_Maquette_liste = config[name].getboolean('img_maquette_liste', False)
    if Img_Maquette_liste :
        Img_Maquette = [e.strip() for e in config[name].get('img_maquette').split(',')]
    else:
        # TODO faire un test si l'image name.png existe alors on la prend ...
        #Img_Maquette = str(config[name].get('img_maquette', name + ".png")) 
        Img_Maquette = str(config[name].get('img_maquette', "defaut.png"))

    Texte_Maquette = str(config[name].get('texte_maquette', 'Maquette'))
    Carte_AllData = config[name].getboolean('carte_alldata', True)
    Carte_MAJ_grouperadio = config[name].getboolean('carte_maj_grouperadio', False)
    Param1 = config[name].get('param1')
    Param2 = config[name].get('param2')
    Param3 = config[name].get('param3')
    # Si on viens depuis http://localhost:5000/external/{name} OU si à la racine exite name.html on prend ce fichier template
    #if template_externe or os.path.exists(name + '.html'):
    if os.path.exists(name + '.html'):
        # si bien template externe et le fichier name.html existe bien à la racine de l'executable
        template_externe = False
        # Charge le fichier template externe
        with open(name + '.html', 'r', encoding='utf-8') as file:
            template_content = file.read()
        return render_template_string(template_content, groupe_radio = groupe_radio, 
            Titre = Titre, Sous_titre = Sous_titre, Carte_AllData = Carte_AllData,
            Carte_MAJ_grouperadio = Carte_MAJ_grouperadio,
            Img_Maquette = Img_Maquette, Img_Maquette_liste = Img_Maquette_liste,
            Data_format = Data_format, Valeur_defaut = Valeur_defaut, Nb_Maquettes = Nb_Maquettes,
            Texte_Maquette = Texte_Maquette, Liste_Maquettes = Liste_Maquettes,
            Param1 = Param1, Param2 = Param2, Param3 = Param3)
    else:
        # si on arrive la et que le template_externe = True => soucis le fichier template name.html n'existe pas !
        #if template_externe :
        #    template_externe = False
        #    abort(404)
        # Charge un template interne
        template_externe = False
        # recupère la page web issu de la config sinon defaut.html
        Page_web = config[name].get('Page_html', "defaut.html")
        # on test si le template name.html existe si oui alors on l'utilise (ex lapin) à la place de defaut.html
        if template_exists(str(name + '.html')):
            Page_web = str(name + '.html')
        print(f" nom page ouverte {Page_web}")
        return render_template(Page_web, groupe_radio = groupe_radio, 
            Titre = Titre, Sous_titre = Sous_titre, Carte_AllData = Carte_AllData,
            Carte_MAJ_grouperadio = Carte_MAJ_grouperadio,
            Img_Maquette = Img_Maquette, Img_Maquette_liste = Img_Maquette_liste,
            Data_format = Data_format, Valeur_defaut = Valeur_defaut, Nb_Maquettes = Nb_Maquettes,
            Texte_Maquette = Texte_Maquette, Liste_Maquettes = Liste_Maquettes,
            Param1 = Param1, Param2 = Param2, Param3 = Param3)

# Lancement du serveur Flask
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)