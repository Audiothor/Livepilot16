# LivePilot 16 — Conception Matérielle & PCB (KiCad v8)

Ce dossier rassemble tous les fichiers de conception électronique du contrôleur **LivePilot 16**.

## 1. Organisation du Répertoire
* `kicad/` : Fichiers sources KiCad 8 (`.kicad_sch` pour le schéma, `.kicad_pcb` pour le routage).
* `gerber/` : Fichiers de fabrication Gerber 274X et perçage Drill prêts à être zippés pour commande (JLCPCB / PCBWay).
* `bom/` : Fichiers de nomenclature au format CSV avec références Mouser / LCSC.
* [`WIRING_GUIDE.md`](WIRING_GUIDE.md) : **Guide de câblage complet broche par broche** de tous les composants du contrôleur.

## 2. Architecture Électronique
* **Microcontrôleur** : ESP32-S3-DevKitC-1-N16R8 enfichable sur barrettes sécables femelles.
* **Bus I2C (400 kHz)** : 
  * 4x MCP23017 (Adresses configurées via A0/A1/A2 : `0x20`, `0x21`, `0x22`, `0x23`).
  * Résistances de pull-up I2C 2.2kΩ sur SDA et SCL.
  * Lignes d'interruption `INTA`/`INTB` reliées aux GPIO 4 et 5 de l'ESP32-S3.
* **Bus SPI Display** :
  * Écran TFT 3.5" ou 4.0" IPS ILI9488 relié aux broches GPIO 10 (CS), 11 (MOSI), 12 (SCK), 13 (DC), 14 (RST), 21 (BL PWM).
* **Matrice de Contrôle** :
  * 16 Encodeurs Bourns PEC11R avec poussoir push intégré.
  * 16 Boutons de pistes avec 16x WS2812B Mini en cascade unifilaire sur GPIO 48 (RMT).
  * 6 Boutons de navigation tactiles (`TRACK -/+`, `GROUP -/+`, `DEVICE -/+`) sur GPIOs 15, 16, 17, 18, 1, 2.
