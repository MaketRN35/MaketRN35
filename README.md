# MaketRN35
Interface Maquettes Micro:Bit radio vers Micro:Bit et serie vers PC

Bien sûr ! Voici une **documentation structurée** pour ton projet [MaketRN35](https://github.com/MaketRN35/MaketRN35) :

---

# 📚 Documentation du projet MaketRN35

## 📝 Description

**MaketRN35** est une interface permettant la communication :
- **Micro:Bit → Micro:Bit** via la radio,
- **Micro:Bit → PC** via la liaison série.

Elle est particulièrement destinée aux maquettes pédagogiques pour transmettre des données depuis des Micro:Bit vers un ordinateur.

---

## 📂 Structure du projet

| Dossier/Fichier | Description |
| :--- | :--- |
| `.github/workflows/` | Contient les workflows GitHub Actions pour l'intégration continue. |
| `static/` | Contient les fichiers statiques pour l'interface web (CSS, JS, images). |
| `templates/` | Contient les templates HTML pour le serveur web. |
| `Changelog.md` | Journal des modifications et versions du projet. |
| `README.md` | Présentation rapide du projet (actuellement minimaliste). |
| `config.ini` | Fichier de configuration du projet (paramètres personnalisables). |
| `microbit-serieversusb.hex` | Firmware à flasher sur la Micro:Bit pour activer la communication série. |
| `microbit_server.py` | Script Python principal qui agit comme serveur pour gérer les communications entre Micro:Bit et PC. |

---

## 🛠️ Installation et lancement

### 1. Prérequis
- Python 3.7+
- Une Micro:Bit (au minimum)
- Câble USB pour connecter la Micro:Bit au PC
- Dépendances Python (`Flask`, etc.)

### 2. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3. Flasher la Micro:Bit
- Télécharger et flasher le fichier `microbit-serieversusb.hex` sur votre Micro:Bit.

### 4. Lancer le serveur
```bash
python microbit_server.py
```

Cela démarre un serveur web local qui permet de recevoir les données de la Micro:Bit.

---

## 🌐 Utilisation

- Connecter la Micro:Bit au PC en USB.
- Ouvrir l'interface web fournie par le serveur (`http://localhost:5000/` par défaut).
- Envoyer/recevoir des données entre Micro:Bits et visualiser les résultats sur l'interface.

---

## 📈 Journal des versions

Consulter `Changelog.md` pour voir l'historique des mises à jour et améliorations.

---

## 📄 Licence

Aucune licence spécifiée pour le moment.

---


Voici une **description détaillée** du fonctionnement du fichier [`microbit_server.py`](https://github.com/MaketRN35/MaketRN35/blob/main/microbit_server.py) :

---

# 📜 Fonctionnement de `microbit_server.py`

## 1. **Objectif principal**
Ce script sert à établir une **passerelle** entre :
- les **Micro:Bit** connectées en USB (port série),
- une **interface web** locale qui permet de consulter les données reçues.

Il utilise **Flask** pour le serveur web et **Flask-SocketIO** pour la communication temps réel avec la page web.

---

## 2. **Modules et bibliothèques utilisés**
- `serial`, `serial.tools.list_ports` : pour communiquer via ports série (USB).
- `flask`, `flask_socketio` : pour construire le serveur web + WebSocket.
- `configparser` : pour lire la configuration depuis `config.ini`.
- `threading` : pour lire les données série en parallèle du serveur web.

---

## 3. **Variables globales**
- `latest_data` : stocke la dernière valeur reçue **toutes maquettes confondues**.
- `All_latest_data` : stocke la dernière valeur **par maquette**.
- `histo_data` : stocke un **historique** des valeurs reçues pour chaque maquette.

---

## 4. **Fonctionnement détaillé**

### a) **Initialisation**
- Lecture du fichier `config.ini` pour configurer :
  - Le **port série** à utiliser.
  - Le **baudrate** (vitesse de communication).
  - Le **port du serveur web**.

### b) **Connexion série**
- Le programme essaie d'ouvrir la connexion au Micro:Bit sur le port série.
- Si plusieurs ports sont disponibles, il choisit celui correspondant aux paramètres ou celui trouvé automatiquement.

### c) **Thread de lecture série**
- Un **thread secondaire** est lancé pour :
  - Lire en continu les lignes reçues du Micro:Bit via la liaison série.
  - Chaque ligne est supposée contenir une information de type :
    ```
    <nom_maquette>:<valeur>
    ```
    Exemple : `ParkingA:2`
  - La valeur est :
    - Stockée dans `All_latest_data`.
    - Ajoutée dans `histo_data` pour garder un historique.
    - Envoyée **en temps réel** à la page web via **SocketIO**.

### d) **Serveur web**
- **Pages HTML** servies via Flask :
  - `/` : Interface principale.
  - `/history` : Voir l'historique des valeurs reçues.
- **SocketIO** :
  - Met à jour l'interface en temps réel dès qu'une nouvelle donnée est reçue.

### e) **API et routes spéciales**
- `/api/latest` : Retourne la dernière valeur reçue (JSON).
- `/api/all_latest` : Retourne toutes les dernières valeurs par maquette (JSON).
- `/api/historique` : Retourne l'historique complet (JSON).

---

## 5. **Fonctions principales**

| Fonction | Rôle |
| :--- | :--- |
| `read_config()` | Lire la configuration dans `config.ini`. |
| `connect_microbit()` | Détecter et ouvrir le port série. |
| `read_from_serial()` | Lire les données en continu depuis la Micro:Bit. |
| `background_thread()` | Thread gérant la lecture série et la mise à jour des données. |
| `create_app()` | Créer l'application Flask + configuration des routes et WebSocket. |

---

## 6. **Résumé du cycle de vie**

1. Le script lance le serveur Flask + SocketIO.
2. En parallèle, un thread lit les données du port série.
3. Les données reçues sont enregistrées et transmises en temps réel à l'interface web.
4. L'utilisateur peut visualiser en live ou consulter l'historique des données.

---
