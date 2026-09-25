# LivePilot 16
> **"Ne regardez plus l'écran, pilotez votre son."**  
> *(Alternative internationale : "Eyes off the screen, hands on the sound.")*

![LivePilot 16 Mockup](doc/assets/livepilot16_mockup.jpg)

**LivePilot 16** est une surface de contrôle matérielle professionnelle pour **Ableton Live**, basée sur l'ESP32-S3 et conçue pour la scène et le studio. Elle permet de naviguer intuitivement et les yeux fermés dans l'arborescence :
$$\text{Projet} \longrightarrow \text{Banque de Pistes} \longrightarrow \text{Piste (Track)} \longrightarrow \text{Plugin (Device)} \longrightarrow \text{16 Paramètres}$$

---

## 📂 Structure du Répertoire (Monorepo Professionnel)

Chaque discipline technique dispose de son propre répertoire totalement autonome :

```
LivePilot16/
├── firmware/              # [ESP32-S3] Projet PlatformIO en C++17 (Drivers, USB-MIDI, TFT, FreeRTOS)
│   ├── platformio.ini     # Configuration PlatformIO (TinyUSB, LovyanGFX, MCP23017)
│   ├── include/           # Headers (config.h, protocol.h)
│   └── src/               # Code source principal (main.cpp Dual-Core)
│
├── remote_script/         # [ABLETON] MIDI Remote Script natif en Python 3
│   └── LivePilot16/       # Package officiel Ableton Live (__init__.py, LivePilot16.py, consts.py)
│
├── hardware/              # [ÉLECTRONIQUE] Conception PCB sous KiCad v8
│   ├── kicad/             # Schémas et typons de routage
│   ├── gerber/            # Fichiers de fabrication pour JLCPCB / PCBWay
│   └── bom/               # Nomenclature détaillée des composants
│
├── enclosure/             # [MÉCANIQUE] Modélisation 3D du châssis incliné 15°
│   ├── openscad/          # Scripts paramétriques OpenSCAD
│   ├── stl/               # Modèles 3D prêts à trancher et imprimer
│   └── step/              # Fichiers CAO neutres pour FreeCAD / Fusion 360
│
├── tools/                 # [UTILITAIRES] Scripts d'automatisation
│   └── install_script.py  # Déploiement en 1 clic dans Ableton Live
│
└── doc/                   # [DOCUMENTATION] Cahier des charges, rendus visuels & specs
    ├── CAHIER_DES_CHARGES.md
    └── assets/
```

---

## 🚀 Démarrage Rapide

### 1. Installation du Remote Script dans Ableton Live
Exécutez simplement le script d'installation automatique :
```bash
python tools/install_script.py
```
Puis, dans **Ableton Live** :
* Allez dans `Options` > `Préférences` > `Link, Tempo & MIDI`.
* Dans la première ligne des **Surfaces de contrôle**, sélectionnez `LivePilot 16`.
* Sélectionnez les ports MIDI `LivePilot 16` en Entrée et Sortie.

### 2. Compilation et Flash du Firmware ESP32-S3
```bash
# Installation de PlatformIO CLI (si non installé)
pip install platformio

# Compilation du firmware
pio run -d firmware

# Téléversement vers l'ESP32-S3 connecté en USB
pio run -d firmware -t upload

# Surveillance du port série
pio device monitor -d firmware
```

---

## 📄 Documentation Complète
Consultez le [Cahier des Charges Technique & Fonctionnel](CAHIER_DES_CHARGES.md) pour retrouver :
* La nomenclature complète (BOM) avec références et liens d'achat exacts.
* L'estimation budgétaire détaillée (~258 € TTC en qualité pro double écran IPS).
* Les spécifications du protocole SysEx et l'ergonomie d'affichage.
