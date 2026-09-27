# LivePilot 16 — Conception Matérielle & PCB (KiCad v8)

Ce dossier rassemble tous les fichiers de conception électronique du contrôleur **LivePilot 16**.

## 1. Organisation du Répertoire
* `kicad/` : Fichiers sources KiCad 8 (`.kicad_sch` pour le schéma, `.kicad_pcb` pour le routage).
* `gerber/` : Fichiers de fabrication Gerber 274X et perçage Drill prêts à être zippés pour commande (JLCPCB / PCBWay).
* `bom/` : Fichiers de nomenclature au format CSV avec références Mouser / LCSC.
* [`WIRING_GUIDE.md`](WIRING_GUIDE.md) : **Guide de câblage complet broche par broche** de tous les composants du contrôleur.

## 2. Architecture Électronique & Schémas Visuels
* Consultez le [**Guide Complet de Câblage Électronique (WIRING_GUIDE.md)**](WIRING_GUIDE.md) pour les schémas complets :
  * **Schéma Électronique Global** : [doc/assets/livepilot16_schematic_system.jpg](../doc/assets/livepilot16_schematic_system.jpg)
  * **Faisceau de Câblage & Interconnexion** : [doc/assets/livepilot16_schematic_wiring_harness.jpg](../doc/assets/livepilot16_schematic_wiring_harness.jpg)
* **Microcontrôleur** : ESP32-S3-DevKitC-1-N16R8 enfichable sur barrettes sécables femelles.
* **Bus I2C Fast Mode (400 kHz)** : 
  * 4x MCP23017 (Adresses physiques : `0x20` Enc 1-8, `0x21` Enc 9-16, `0x22` 16 Pads RGB, `0x23` 16 Poussoirs).
  * Résistances de pull-up I2C 2.2kΩ sur SDA (GPIO 8) et SCL (GPIO 9).
  * Lignes d'interruption `INTA`/`INTB` reliées aux GPIO 4 et 5 de l'ESP32-S3.
* **Bus SPI Display (40 MHz)** :
  * Double écran TFT 3.5" IPS ILI9488 relié aux broches GPIO 10 (CS Gauche), GPIO 38 (CS Droit), 11 (MOSI), 12 (SCK), 13 (DC), 14 (RST), 21 (BL PWM).
* **Commandes Physiques & Contrôle Direct** :
  * 16 Encodeurs de paramètres Bourns PEC11R (2x8).
  * 17ᵉ Encodeur Master (Jog / BPM / Menu) relié directement aux GPIOs 40, 41 et poussoir 39.
  * Bouton dédié `[VALID]` relié directement au GPIO 42.
  * 16 Touches de sélection de pistes avec 16x WS2812B Mini en guirlande unifilaire sur GPIO 48 (RMT).
  * 8 Boutons de navigation dédiés en colonne 4×2 (`◄/►`, `GROUP -/+`, `DEVICE -/+`, `TRACK -/+`) avec large espacement de sécurité anti-erreur sur GPIOs 6, 7, 17, 18, 1, 2, 15, 16.
