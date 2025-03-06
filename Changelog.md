# Changelog

Programme développé par Anthony PENHARD pour piloter des maquettes en classe de technologie Collège Ac-Rennes
avec carte BBC Micro:Bit qui communiques en "sans-fil" et permet d'avoir une supervisions de chaques maquettes via une interface web locale

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)


## [2.2.0] - 2025-03-05

### Added
 - ajout historisation de la "dernière valeurs reçues" All_latest_data ; mais aussi l'historique complet des valeurs histo_data  
 - si nouvelle page affichée/connectée au socket, met a jour celle-ci avec les dernières valeurs historisées All_latest_data
 - nouveau template "/charts/<data>" permet de générer un graphique des 20 dernières valeur reçue de type <data>:val dans histo_data
 	- ce nouveau template peux être appelé via "iframe" dans un autre template 
 - lors d'appel, si un ou des paramètres ajouter en "get" "ex. http://localhost:5000/parking?Img_Maquette=parking.jpg&Texte_Maquette=Parking&Data_format=Parking" prend donc par défaut ces paramètres à la place de la configuration 
 - ajout de "block" dans le template "defaut" qui permet de créer des templates par "héritage" 
 	- block : css_perso / carte_Maquette / perso_Maquette (dans carte_Maquette) / body_perso / javascript_perso / socket_update_data

### Changed
 - modification de la fonction charts, utilise les données de histo_data et aussi les nouvelles à venir via socket
 - "/potager" : ajout de seuils pour chaque potager et aussi une iframe qui affiche le graph "historique des 20 dernières valeures" 
### Deprecated
 - la fonction "http://localhost:5000/external/<template>" ne sert plus, car géré directement "http://localhost:5000/<template>", va chercher le template disponible à la racine de l'executable si disponible ou natif ou "defaut"


## [2.1.0] - 2025-02-22

### Added
- Ajout template spécifique pour "8 maquettes Potager connecté"" "/potager" (Demande de Dave E.)
- Ajout parking trottinette v2 "/trott2" savoir quelles sont les places libres (Demande de Dave E.)
- gérer de façon générique une page template perso.html si existent à coté du script et dans le config.ini
   alors le lancer par défaut et via serveur web si localhost:5000/perso ouvrir la page perso.html si existe au lieu de "defaut.html"
- standardisation sections config.ini pour un template personalisé :
[defaut]
// format des données de type : <Data_format>X:Y  avec X dans <Liste_Ilot> et Y valeur fonctionnelle pour la maquette
Titre : Maquette de Machin truc
Sous_titre : maquette qui mesure un machin
// format des données de type : <Data_format>X:Y  avec X dans <Liste_Ilot> et Y valeur fonctionnelle pour la maquette
Data_format : H
// Y : Valeur par défaut reçue pour les maquettes
Valeur_defaut : 100
// liste des "noms" de chaque maquettes possible cartères chiffres ou lettres ou mélangé
Liste_Maquettes : 01, 02, 03, 04, 05, 06, 07, 08, 09, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20
// Nombre de maquettes à afficher sur page web 
Nb_Maquettes : 16
// Page web a afficher ( par défaut nom de la maquette <name>.hmtl )
Page_html : defaut.html
// Page web texte pour chaque Maquette
Texte_Maquette : Maquette
// image a afficher pour chauqe maquette dans la Page web <name>XX.png 
// (defaut.png, carte.png, parking.jpg, bipeur.png, potager.png , potager(1 à 8).png, barriere.png, trott2_(0 à 7).png)
Img_Maquette : potager1.png, potager2.png, potager3.png, potager4.png, potager5.png, potager6.png, potager7.png, potager8.png
// image a afficher si liste true OU false affiche la même image pour chacun et donc Img_Maquette n'a qu'1 image
Img_Maquette_liste : true
// affiche la carte qui affiche la dernière data reçue par défaut true
Carte_AllData : true
// affiche la carte pour modifier le Groupe Radio utilisé par défaut false
Carte_MAJ_grouperadio : true
// Paramètres "autres" envoyés au serveur web 
Param1 : 1
Param2 : 2
Param3 : 3
- Images 'static' présentes :
favicon.png
defaut.png
carte.png
parking.jpg
potager.png
potager(1à8).png
trott2_(0à7).png
bipeur.png
barriere.png
karotz.jpg
- Templates intégrés :
config
index (page par défaut racine du serveur web)
defaut
lapin ( perso et tests pour Anthony P.)
potager ( potager connecté David E.)
trott2 ( parking trottinette v2 David E.)


### Removed
- Les pages/templates spécifiques (Rfid, Parking trotinettes "trott" ) => standardisation de tous ces templates spécifiques
- Configuration spécifique des maquettes parking trotinettes

### Changed
- fichier config.ini : la section "settings" est la configuration générale du script
[settings]  
serial_port : COM4 // Windows (ex: "COM5")
cnx_auto : on //connexion automatique du port série On True (par défaut) /False Off 
baud_rate : 115200 // vistesse de connexion série
groupe_radio : 99 // groupe radio utilisé par les cartes Micro:Bit

- si fichier config pas présent et/ou partiel il y a des valeurs par défaut prises pour chaque paramètres
- suppresion de la config spécifique au parking de trotinette pour standardisation


## [2.0.3] - 2025-02-18

### Added
 réfelxion sur le nom et dépot sur un github : MaketRN35 ( https://github.com/MaketRN35/MaketRN35 )
V2_0_2 : 05/02/25 : ajout a config.ini les données pour le parking trottinette
V2_0_1 : 04/02/25 : si fichier config.ini absent, défini par défaut une config
V2_0_0 : 02/02/25 : ajout fichier du websocket au lieu d'un pooling toutes les 1s, j'ai gardé la section api pour envoyer à la MB

V1_0_1 à 1_0_3 : 23/01/25 : 
	- ajout page Config et amélioration de index avec 20 cartes affichées
	- ajout page RFID avec 09 ilôts
	- ajout fichier de config.ini + pas mal de templates ...
V1_0_0 : 22/01/25 : initiale prend le dernier pour COM pour afficher valeures reçu et possible envoi manuellement datas




### Added
 pour les nouvelles fonctionnalités. 
### Changed
 pour les changements aux fonctionnalités préexistantes. 
### Deprecated
 pour les fonctionnalités qui seront bientôt supprimées
### Removed
 pour les fonctionnalités désormais supprimées. 
### Fixed
 pour les corrections de bugs. 