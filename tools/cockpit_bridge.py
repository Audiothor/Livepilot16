#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilot 16 — Simulateur / Serveur de test autonome (Live Cockpit Bridge)
Permet de visualiser l'interface sur la tablette Android (ou navigateur PC)
et de tester l'ensemble du dashboard sans avoir besoin d'ouvrir Ableton Live.

Prend en charge :
- La grille 16 pistes (8x2) avec VU-mètres stéréo animés en temps réel
- Le bandeau scénique Hero 3 cartes (01 - Intro / 02 - Couplet / 03 - Refrain)
- La nouvelle section latérale DEVICES / PLUGINS en rectangles empilés
- Le contour Cyan néon (#00f0ff) et badge ACTIF pour le plugin sélectionné
- La navigation ◀ Précédent / Suivant ▶ avec mise à jour immédiate des 24 encodeurs macro
- Le master VU-mètre calibré (MAIN : -0.2 dB)
"""

import os
import sys
import time
import math
import random
import threading
import webbrowser

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remote_script", "LivePilot16")))
from web_server import LivePilotWebServer

# =============================================================================
# PROFILS DE PARAMÈTRES POUR CHACUN DES PLUGINS (24 Encodeurs)
# =============================================================================
DEVICE_PARAM_PROFILES = {
    "EQ Eight": [
        {"name": "Low Cut", "val": 0.20, "str": "32 Hz"},
        {"name": "Freq 1", "val": 0.35, "str": "120 Hz"},
        {"name": "Gain 1", "val": 0.52, "str": "+1.2 dB"},
        {"name": "Q 1", "val": 0.45, "str": "0.71"},
        {"name": "Freq 2", "val": 0.48, "str": "450 Hz"},
        {"name": "Gain 2", "val": 0.42, "str": "-2.5 dB"},
        {"name": "Q 2", "val": 0.50, "str": "1.00"},
        {"name": "Freq 3", "val": 0.65, "str": "2.5 kHz"},
        {"name": "Gain 3", "val": 0.60, "str": "+3.0 dB"},
        {"name": "Q 3", "val": 0.55, "str": "1.20"},
        {"name": "Freq 4", "val": 0.82, "str": "8.0 kHz"},
        {"name": "Gain 4", "val": 0.48, "str": "-0.8 dB"},
        {"name": "Q 4", "val": 0.40, "str": "0.65"},
        {"name": "High Cut", "val": 0.88, "str": "18 kHz"},
        {"name": "Output", "val": 0.70, "str": "0.0 dB"},
        {"name": "Scale", "val": 0.75, "str": "100 %"},
        {"name": "Mid/Side", "val": 0.00, "str": "Stereo"},
        {"name": "Stereo", "val": 1.00, "str": "On"},
        {"name": "Audition", "val": 0.00, "str": "Off"},
        {"name": "Reso Freq", "val": 0.50, "str": "Flat"},
        {"name": "Soft Clip", "val": 1.00, "str": "On"},
        {"name": "Dyn EQ", "val": 0.30, "str": "30 %"},
        {"name": "Phase Inv", "val": 0.00, "str": "Off"},
        {"name": "Dry/Wet", "val": 1.00, "str": "100 %"}
    ],
    "Serum": [
        {"name": "Cutoff", "val": 0.72, "str": "72 %"},
        {"name": "Resonance", "val": 0.28, "str": "28 %"},
        {"name": "Drive", "val": 0.54, "str": "54 %"},
        {"name": "Sub Level", "val": 0.81, "str": "81 %"},
        {"name": "Noise", "val": 0.23, "str": "23 %"},
        {"name": "FM Amount", "val": 0.46, "str": "46 %"},
        {"name": "Osc Blend", "val": 0.67, "str": "67 %"},
        {"name": "Pan", "val": 0.50, "str": "C"},
        {"name": "Attack", "val": 0.12, "str": "12 %"},
        {"name": "Decay", "val": 0.58, "str": "58 %"},
        {"name": "Sustain", "val": 0.76, "str": "76 %"},
        {"name": "Release", "val": 0.34, "str": "34 %"},
        {"name": "Env Amount", "val": 0.62, "str": "62 %"},
        {"name": "LFO 1 Rate", "val": 0.48, "str": "48 %"},
        {"name": "LFO 1 Amt", "val": 0.55, "str": "55 %"},
        {"name": "LFO 2 Rate", "val": 0.39, "str": "39 %"},
        {"name": "LFO 2 Amt", "val": 0.21, "str": "21 %"},
        {"name": "Warp", "val": 0.66, "str": "66 %"},
        {"name": "Filter Env", "val": 0.43, "str": "43 %"},
        {"name": "Unison", "val": 0.75, "str": "75 %"},
        {"name": "Detune", "val": 0.31, "str": "31 %"},
        {"name": "Width", "val": 0.59, "str": "59 %"},
        {"name": "Delay Mix", "val": 0.22, "str": "22 %"},
        {"name": "Reverb Mix", "val": 0.68, "str": "68 %"}
    ],
    "Compressor": [
        {"name": "Threshold", "val": 0.45, "str": "-16 dB"},
        {"name": "Ratio", "val": 0.60, "str": "4:1"},
        {"name": "Attack", "val": 0.25, "str": "15 ms"},
        {"name": "Release", "val": 0.40, "str": "120 ms"},
        {"name": "Knee", "val": 0.30, "str": "Soft"},
        {"name": "Dry/Wet", "val": 0.85, "str": "85 %"},
        {"name": "Makeup", "val": 0.55, "str": "+3.5 dB"},
        {"name": "Lookahead", "val": 0.10, "str": "1 ms"},
        {"name": "Sidechain", "val": 0.00, "str": "Off"},
        {"name": "SC Freq", "val": 0.35, "str": "110 Hz"},
        {"name": "SC Gain", "val": 0.50, "str": "0 dB"},
        {"name": "SC Listen", "val": 0.00, "str": "Off"},
        {"name": "Peak/RMS", "val": 0.70, "str": "Peak"},
        {"name": "Expander", "val": 0.00, "str": "Off"},
        {"name": "Auto Rel", "val": 1.00, "str": "On"},
        {"name": "Gain Red", "val": 0.38, "str": "-4.2 dB"},
        {"name": "Input", "val": 0.70, "str": "-0.5 dB"},
        {"name": "Output", "val": 0.72, "str": "0.0 dB"},
        {"name": "Hold", "val": 0.15, "str": "25 ms"},
        {"name": "HPF", "val": 0.20, "str": "80 Hz"},
        {"name": "Stereo Link", "val": 1.00, "str": "100 %"},
        {"name": "Transfer", "val": 0.50, "str": "Linear"},
        {"name": "Saturation", "val": 0.25, "str": "Warm"},
        {"name": "Limiter", "val": 0.00, "str": "Off"}
    ],
    "Echo": [
        {"name": "Delay L", "val": 0.38, "str": "3/16"},
        {"name": "Delay R", "val": 0.45, "str": "1/8 D"},
        {"name": "Sync", "val": 1.00, "str": "Sync"},
        {"name": "Feedback", "val": 0.52, "str": "52 %"},
        {"name": "Dry/Wet", "val": 0.40, "str": "40 %"},
        {"name": "Filter HP", "val": 0.25, "str": "120 Hz"},
        {"name": "Filter LP", "val": 0.75, "str": "6.5 kHz"},
        {"name": "Resonance", "val": 0.30, "str": "1.2"},
        {"name": "Wobble", "val": 0.45, "str": "Tape"},
        {"name": "Morph", "val": 0.60, "str": "60 %"},
        {"name": "Noise", "val": 0.15, "str": "15 %"},
        {"name": "Gate", "val": 0.00, "str": "Off"},
        {"name": "Reverb Mix", "val": 0.35, "str": "35 %"},
        {"name": "Ducking", "val": 0.20, "str": "-3 dB"},
        {"name": "Mod Depth", "val": 0.55, "str": "55 %"},
        {"name": "Mod Rate", "val": 0.40, "str": "0.8 Hz"},
        {"name": "Phase", "val": 0.50, "str": "180°"},
        {"name": "Stereo Mode", "val": 1.00, "str": "Wide"},
        {"name": "Ping Pong", "val": 1.00, "str": "On"},
        {"name": "Clipper", "val": 0.30, "str": "Soft"},
        {"name": "Offset", "val": 0.12, "str": "12 ms"},
        {"name": "Time L", "val": 0.33, "str": "250 ms"},
        {"name": "Time R", "val": 0.33, "str": "375 ms"},
        {"name": "Output", "val": 0.80, "str": "0 dB"}
    ],
    "Utility": [
        {"name": "Gain", "val": 0.50, "str": "0.0 dB"},
        {"name": "Pan", "val": 0.50, "str": "C"},
        {"name": "Width", "val": 0.80, "str": "100 %"},
        {"name": "Mute", "val": 0.00, "str": "Off"},
        {"name": "Phase L", "val": 0.00, "str": "Normal"},
        {"name": "Phase R", "val": 0.00, "str": "Normal"},
        {"name": "Bass Mono", "val": 1.00, "str": "On"},
        {"name": "Mono Freq", "val": 0.35, "str": "120 Hz"},
        {"name": "DC Offset", "val": 0.00, "str": "Filter"},
        {"name": "Solo L", "val": 0.00, "str": "Off"},
        {"name": "Solo R", "val": 0.00, "str": "Off"},
        {"name": "Channel Swap", "val": 0.00, "str": "L/R"},
        {"name": "Clip Guard", "val": 1.00, "str": "On"},
        {"name": "Headroom", "val": 0.70, "str": "+6 dB"},
        {"name": "Output", "val": 0.75, "str": "0 dB"},
        {"name": "Smoothing", "val": 0.50, "str": "Fast"},
        {"name": "Invert", "val": 0.00, "str": "Off"},
        {"name": "Trim", "val": 0.50, "str": "0 dB"},
        {"name": "Sub Balance", "val": 0.50, "str": "C"},
        {"name": "Low Pan", "val": 0.50, "str": "C"},
        {"name": "High Pan", "val": 0.50, "str": "C"},
        {"name": "Link L/R", "val": 1.00, "str": "Linked"},
        {"name": "Dim", "val": 0.00, "str": "Off"},
        {"name": "Range", "val": 0.85, "str": "Full"}
    ]
}

def build_params(dev_name):
    profile = DEVICE_PARAM_PROFILES.get(dev_name)
    if profile:
        return [{"index": i, "name": p["name"], "value": p["val"], "str": p["str"]} for i, p in enumerate(profile)]
    return [{"index": i, "name": f"Param {i+1}", "value": 0.50, "str": "50 %"} for i in range(24)]

# =============================================================================
# DONNÉES DE SIMULATION COCKPIT (64 PISTES SUR 4 BANQUES)
# =============================================================================
ALL_DEMO_TRACKS = [
    # BANQUE 1 (Pistes 1 à 16 : Pistes de base)
    {"index": 0, "name": "Drums", "color": "#ff2a5f", "is_group": True, "vol_str": "-6.2 dB", "pan_val": 0.0},
    {"index": 1, "name": "Bass", "color": "#ffd000", "is_group": False, "vol_str": "-4.1 dB", "pan_val": 0.0},
    {"index": 2, "name": "Pads", "color": "#2979ff", "is_group": False, "vol_str": "-8.3 dB", "pan_val": 0.0},
    {"index": 3, "name": "Lead", "color": "#b388ff", "is_group": False, "vol_str": "-10.5 dB", "pan_val": 0.0},
    {"index": 4, "name": "FX", "color": "#00e676", "is_group": False, "vol_str": "-12.0 dB", "pan_val": 0.0},
    {"index": 5, "name": "Vocals", "color": "#ff4081", "is_group": False, "vol_str": "-7.1 dB", "pan_val": 0.0},
    {"index": 6, "name": "Guitar", "color": "#ff9100", "is_group": False, "vol_str": "-9.6 dB", "pan_val": 0.0},
    {"index": 7, "name": "Keys", "color": "#00e5ff", "is_group": False, "vol_str": "-11.4 dB", "pan_val": 0.0},
    {"index": 8, "name": "Perc", "color": "#7c4dff", "is_group": False, "vol_str": "-5.8 dB", "pan_val": 0.0},
    {"index": 9, "name": "Stabs", "color": "#76ff03", "is_group": False, "vol_str": "-14.1 dB", "pan_val": 0.0},
    {"index": 10, "name": "Atmos", "color": "#00b0ff", "is_group": False, "vol_str": "-11.2 dB", "pan_val": 0.0},
    {"index": 11, "name": "Arp", "color": "#f50057", "is_group": False, "vol_str": "-9.0 dB", "pan_val": 0.0},
    {"index": 12, "name": "Brass", "color": "#1de9b6", "is_group": False, "vol_str": "-16.3 dB", "pan_val": 0.0},
    {"index": 13, "name": "Strings", "color": "#ff6e40", "is_group": False, "vol_str": "-16.6 dB", "pan_val": 0.0},
    {"index": 14, "name": "Synths", "color": "#d500f9", "is_group": True, "vol_str": "-8.9 dB", "pan_val": 0.0},
    {"index": 15, "name": "Vox FX", "color": "#00bcd4", "is_group": False, "vol_str": "-12.7 dB", "pan_val": 0.0},

    # BANQUE 2 (Pistes 17 à 32 : Éléments rythmiques & synthés)
    {"index": 16, "name": "Kick", "color": "#ff2a5f", "is_group": False, "vol_str": "-3.0 dB", "pan_val": 0.0},
    {"index": 17, "name": "Snare", "color": "#ff5252", "is_group": False, "vol_str": "-4.5 dB", "pan_val": 0.0},
    {"index": 18, "name": "HiHat", "color": "#ffd54f", "is_group": False, "vol_str": "-8.0 dB", "pan_val": 0.1},
    {"index": 19, "name": "Perc 2", "color": "#ffa726", "is_group": False, "vol_str": "-7.5 dB", "pan_val": -0.2},
    {"index": 20, "name": "808 Sub", "color": "#ffd000", "is_group": False, "vol_str": "-2.8 dB", "pan_val": 0.0},
    {"index": 21, "name": "Reese", "color": "#ff9800", "is_group": False, "vol_str": "-6.0 dB", "pan_val": 0.0},
    {"index": 22, "name": "Pluck", "color": "#2979ff", "is_group": False, "vol_str": "-9.2 dB", "pan_val": 0.15},
    {"index": 23, "name": "Bell", "color": "#00e5ff", "is_group": False, "vol_str": "-11.0 dB", "pan_val": -0.15},
    {"index": 24, "name": "Choir", "color": "#b388ff", "is_group": False, "vol_str": "-13.5 dB", "pan_val": 0.0},
    {"index": 25, "name": "Strings 2", "color": "#9575cd", "is_group": False, "vol_str": "-12.0 dB", "pan_val": 0.2},
    {"index": 26, "name": "Horns", "color": "#1de9b6", "is_group": False, "vol_str": "-10.0 dB", "pan_val": -0.1},
    {"index": 27, "name": "Impact", "color": "#00e676", "is_group": False, "vol_str": "-8.0 dB", "pan_val": 0.0},
    {"index": 28, "name": "Sweep", "color": "#26c6da", "is_group": False, "vol_str": "-9.5 dB", "pan_val": 0.0},
    {"index": 29, "name": "Riser", "color": "#42a5f5", "is_group": False, "vol_str": "-7.0 dB", "pan_val": 0.0},
    {"index": 30, "name": "Noise", "color": "#78909c", "is_group": False, "vol_str": "-14.0 dB", "pan_val": 0.0},
    {"index": 31, "name": "Sub Drop", "color": "#ff4081", "is_group": False, "vol_str": "-5.0 dB", "pan_val": 0.0},

    # BANQUE 3 (Pistes 33 à 48 : Harmonies, Voix & Acoustique)
    {"index": 32, "name": "Lead Vox", "color": "#ff4081", "is_group": False, "vol_str": "-4.0 dB", "pan_val": 0.0},
    {"index": 33, "name": "Back Vox 1", "color": "#f06292", "is_group": False, "vol_str": "-9.0 dB", "pan_val": -0.3},
    {"index": 34, "name": "Back Vox 2", "color": "#f06292", "is_group": False, "vol_str": "-9.0 dB", "pan_val": 0.3},
    {"index": 35, "name": "Harmony L", "color": "#ba68c8", "is_group": False, "vol_str": "-10.5 dB", "pan_val": -0.4},
    {"index": 36, "name": "Harmony R", "color": "#ba68c8", "is_group": False, "vol_str": "-10.5 dB", "pan_val": 0.4},
    {"index": 37, "name": "Acoustic Gtr", "color": "#ff9100", "is_group": False, "vol_str": "-8.2 dB", "pan_val": -0.2},
    {"index": 38, "name": "Electric Gtr", "color": "#ffa726", "is_group": False, "vol_str": "-7.5 dB", "pan_val": 0.25},
    {"index": 39, "name": "Grand Piano", "color": "#00e5ff", "is_group": False, "vol_str": "-6.8 dB", "pan_val": 0.0},
    {"index": 40, "name": "Rhodes", "color": "#26c6da", "is_group": False, "vol_str": "-8.5 dB", "pan_val": 0.1},
    {"index": 41, "name": "Hammond", "color": "#4db6ac", "is_group": False, "vol_str": "-9.0 dB", "pan_val": -0.15},
    {"index": 42, "name": "Clavinet", "color": "#81c784", "is_group": False, "vol_str": "-11.0 dB", "pan_val": 0.2},
    {"index": 43, "name": "Shaker", "color": "#aed581", "is_group": False, "vol_str": "-12.5 dB", "pan_val": 0.3},
    {"index": 44, "name": "Tambourine", "color": "#dce775", "is_group": False, "vol_str": "-13.0 dB", "pan_val": -0.25},
    {"index": 45, "name": "Claps", "color": "#fff176", "is_group": False, "vol_str": "-6.5 dB", "pan_val": 0.0},
    {"index": 46, "name": "Snaps", "color": "#ffd54f", "is_group": False, "vol_str": "-9.0 dB", "pan_val": 0.05},
    {"index": 47, "name": "Foley", "color": "#90a4ae", "is_group": False, "vol_str": "-15.0 dB", "pan_val": 0.0},

    # BANQUE 4 (Pistes 49 à 64 : Orchestral, Cuivres, Bois & Percussions Live)
    {"index": 48, "name": "Trumpets", "color": "#ffd000", "is_group": False, "vol_str": "-5.5 dB", "pan_val": -0.2},
    {"index": 49, "name": "Trombones", "color": "#ffb300", "is_group": False, "vol_str": "-6.2 dB", "pan_val": 0.2},
    {"index": 50, "name": "French Horn", "color": "#ff8f00", "is_group": False, "vol_str": "-7.8 dB", "pan_val": -0.15},
    {"index": 51, "name": "Tuba", "color": "#e65100", "is_group": False, "vol_str": "-4.5 dB", "pan_val": 0.0},
    {"index": 52, "name": "Sax Alto", "color": "#00e676", "is_group": False, "vol_str": "-6.0 dB", "pan_val": -0.1},
    {"index": 53, "name": "Sax Tenor", "color": "#00c853", "is_group": False, "vol_str": "-6.5 dB", "pan_val": 0.15},
    {"index": 54, "name": "Flutes", "color": "#69f0ae", "is_group": False, "vol_str": "-10.2 dB", "pan_val": 0.0},
    {"index": 55, "name": "Clarinets", "color": "#00b0ff", "is_group": False, "vol_str": "-11.0 dB", "pan_val": -0.25},
    {"index": 56, "name": "Violins 1", "color": "#2979ff", "is_group": False, "vol_str": "-8.0 dB", "pan_val": -0.35},
    {"index": 57, "name": "Violins 2", "color": "#3d5afe", "is_group": False, "vol_str": "-8.5 dB", "pan_val": -0.2},
    {"index": 58, "name": "Violas", "color": "#651fff", "is_group": False, "vol_str": "-9.0 dB", "pan_val": 0.2},
    {"index": 59, "name": "Cellos", "color": "#7c4dff", "is_group": False, "vol_str": "-7.2 dB", "pan_val": 0.3},
    {"index": 60, "name": "Double Bass", "color": "#b388ff", "is_group": False, "vol_str": "-5.0 dB", "pan_val": 0.0},
    {"index": 61, "name": "Brass Orch", "color": "#1de9b6", "is_group": True, "vol_str": "-4.2 dB", "pan_val": 0.0},
    {"index": 62, "name": "Timpani", "color": "#ff5252", "is_group": False, "vol_str": "-6.0 dB", "pan_val": 0.0},
    {"index": 63, "name": "Tubular Bell", "color": "#ff4081", "is_group": False, "vol_str": "-11.5 dB", "pan_val": 0.05}
]

def get_bank_tracks(bank_index):
    start_idx = max(0, min(3, bank_index)) * 16
    end_idx = start_idx + 16
    return ALL_DEMO_TRACKS[start_idx:end_idx]

DEMO_TRACKS = ALL_DEMO_TRACKS[:16]

TRACK_DEVICES_MAP = {
    0: [{"index": 0, "name": "Drum Rack"}, {"index": 1, "name": "Glue Comp"}, {"index": 2, "name": "Saturator"}, {"index": 3, "name": "EQ Eight"}],
    1: [{"index": 0, "name": "EQ Eight"}, {"index": 1, "name": "Serum"}, {"index": 2, "name": "Compressor"}, {"index": 3, "name": "Echo"}, {"index": 4, "name": "Utility"}],
    2: [{"index": 0, "name": "Wavetable"}, {"index": 1, "name": "Chorus-Ensemble"}, {"index": 2, "name": "Reverb"}, {"index": 3, "name": "EQ Eight"}],
    3: [{"index": 0, "name": "Analog"}, {"index": 1, "name": "Overdrive"}, {"index": 2, "name": "Delay"}, {"index": 3, "name": "Limiter"}]
}

DEFAULT_DEVICES = [
    {"index": 0, "name": "EQ Eight"},
    {"index": 1, "name": "Serum"},
    {"index": 2, "name": "Compressor"},
    {"index": 3, "name": "Echo"},
    {"index": 4, "name": "Utility"}
]

DEMO_SCENES = [
    {"index": 0, "num": 1, "name": "01 - Intro", "color": "#2979ff"},
    {"index": 1, "num": 2, "name": "02 - Couplet", "color": "#00e676"},
    {"index": 2, "num": 3, "name": "03 - Refrain", "color": "#ff2a5f"},
    {"index": 3, "num": 4, "name": "04 - Pont", "color": "#b388ff"},
    {"index": 4, "num": 5, "name": "05 - Solo", "color": "#ffd000"},
    {"index": 5, "num": 6, "name": "06 - Outro", "color": "#00e5ff"}
]

# =============================================================================
# SIMULATEUR SERVEUR
# =============================================================================
def run_simulator(open_browser=False):
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass

    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remote_script", "LivePilot16", "web"))
    server = LivePilotWebServer(port=8080, web_dir=web_dir)

    if not server.start():
        print("[ERREUR] Impossible de lancer le serveur Web sur le port 8080.")
        return

    ips = server.get_local_ips()
    print("=" * 70)
    print("  LIVEPILOT 16 COCKPIT -- SERVEUR DE SIMULATION AUTONOME ACTIF")
    print("=" * 70)
    print("  Affichage tablette (Connectez votre tablette en Wi-Fi au meme reseau) :")
    for ip in ips:
        print(f"    -> http://{ip}:{server.port}")
    print("\n  Affichage sur ce PC :")
    print(f"    -> http://localhost:{server.port}")
    print("-" * 70)
    print("  Fonctionnalites simulees actives :")
    print("  [x] Grille 16 pistes (8x2) avec VU-metres dynamiques et repere 0 dB")
    print("  [x] Bandeau Scene 3 cartes Hero avec lecture interactive")
    print("  [x] Section DEVICES/PLUGINS en rectangles empiles avec contour Cyan neon")
    print("  [x] Navigation rapide [Precedent] / [Suivant] avec bascule des 24 Knobs")
    print("  [x] Master VU-metre stereo calibre (MAIN : -0.2 dB)")
    print("=" * 70)
    print("  Appuyez sur [Ctrl + C] dans cette console pour arreter le serveur.")
    print("=" * 70)

    # État interactif du simulateur
    state = {
        "selected_track_index": 1,
        "bank_index": 0,
        "active_device_index": 1,
        "is_playing": True,
        "active_scene_index": 1,
        "master_vol": 0.825
    }

    def get_track_devices(track_idx):
        return TRACK_DEVICES_MAP.get(track_idx, DEFAULT_DEVICES)

    def broadcast_full_sync():
        cur_bank = state.get("bank_index", 0)
        bank_tracks = get_bank_tracks(cur_bank)
        sel_idx = state["selected_track_index"]
        devs = get_track_devices(sel_idx)
        d_idx = min(state["active_device_index"], len(devs) - 1)
        cur_dev = devs[d_idx]
        cur_params = build_params(cur_dev["name"])

        sc_idx = state["active_scene_index"]
        cur_sc = DEMO_SCENES[sc_idx]
        prev_sc = DEMO_SCENES[max(0, sc_idx - 1)]
        next_sc = DEMO_SCENES[min(len(DEMO_SCENES) - 1, sc_idx + 1)]

        server.broadcast({
            "type": "full_sync",
            "data": {
                "tempo": 120.0,
                "signature": "4 / 4",
                "is_playing": state["is_playing"],
                "play_status": "PLAY" if state["is_playing"] else "STOP",
                "position": "17.2.1",
                "master_volume": {"value": state["master_vol"], "str": "-0.2 dB"},
                "active_scene": {
                    "num": cur_sc["num"],
                    "total": len(DEMO_SCENES),
                    "name": cur_sc["name"],
                    "prev_num": prev_sc["num"],
                    "prev_name": prev_sc["name"],
                    "next_num": next_sc["num"],
                    "next_name": next_sc["name"]
                },
                "scenes": DEMO_SCENES,
                "bank_index": cur_bank,
                "total_banks": 4,
                "selected_track_index": sel_idx,
                "tracks": bank_tracks,
                "devices": devs,
                "active_device_index": d_idx,
                "active_device_name": cur_dev["name"],
                "parameters": cur_params
            }
        })

    def on_message(msg):
        action = msg.get("action")

        if action == "request_full_sync":
            broadcast_full_sync()

        elif action in ("switch_bank", "select_bank"):
            b_idx = int(msg.get("bank", msg.get("bank_index", 0)))
            state["bank_index"] = max(0, min(3, b_idx))
            start_t = state["bank_index"] * 16
            end_t = start_t + 16
            if not (start_t <= state["selected_track_index"] < end_t):
                state["selected_track_index"] = start_t
            broadcast_full_sync()

        elif action == "select_track":
            t_idx = int(msg.get("track_index", 0))
            state["selected_track_index"] = max(0, min(63, t_idx))
            state["bank_index"] = state["selected_track_index"] // 16
            devs = get_track_devices(state["selected_track_index"])
            state["active_device_index"] = 0
            cur_dev = devs[0]
            cur_params = build_params(cur_dev["name"])
            bank_tracks = get_bank_tracks(state["bank_index"])

            server.broadcast({
                "type": "track_selected",
                "data": {
                    "track_index": state["selected_track_index"],
                    "bank_index": state["bank_index"],
                    "tracks": bank_tracks,
                    "devices": devs,
                    "active_device_name": cur_dev["name"],
                    "active_device_index": 0,
                    "parameters": cur_params
                }
            })

        elif action in ("select_device", "select_relative_device"):
            devs = get_track_devices(state["selected_track_index"])
            if action == "select_device":
                d_idx = int(msg.get("device_index", 0))
            else:
                offset = int(msg.get("offset", 1))
                d_idx = state["active_device_index"] + offset

            if 0 <= d_idx < len(devs):
                state["active_device_index"] = d_idx
                cur_dev = devs[d_idx]
                cur_params = build_params(cur_dev["name"])

                server.broadcast({
                    "type": "device_selected",
                    "data": {
                        "device_index": d_idx,
                        "device_name": cur_dev["name"],
                        "parameters": cur_params
                    }
                })

        elif action in ("set_parameter", "set_param_value"):
            p_idx = int(msg.get("index", 0))
            val = float(msg.get("value", 0.5))
            server.broadcast({
                "type": "param_value",
                "data": {
                    "index": p_idx,
                    "value": round(val, 3),
                    "str": f"{int(val * 100)} %"
                }
            })

        elif action in ("fire_scene", "fire_relative_scene"):
            if action == "fire_scene":
                target = int(msg.get("scene_index", 0))
            else:
                offset = int(msg.get("offset", 1))
                target = state["active_scene_index"] + offset

            if 0 <= target < len(DEMO_SCENES):
                state["active_scene_index"] = target
                cur_sc = DEMO_SCENES[target]
                prev_sc = DEMO_SCENES[max(0, target - 1)]
                next_sc = DEMO_SCENES[min(len(DEMO_SCENES) - 1, target + 1)]

                server.broadcast({
                    "type": "scene",
                    "data": {
                        "num": cur_sc["num"],
                        "total": len(DEMO_SCENES),
                        "name": cur_sc["name"],
                        "prev_num": prev_sc["num"],
                        "prev_name": prev_sc["name"],
                        "next_num": next_sc["num"],
                        "next_name": next_sc["name"]
                    }
                })

        elif action == "toggle_play":
            state["is_playing"] = not state["is_playing"]
            server.broadcast({
                "type": "transport",
                "data": {
                    "is_playing": state["is_playing"],
                    "play_status": "PLAY" if state["is_playing"] else "STOP",
                    "tempo": 120.0
                }
            })

    server.on_client_message = on_message

    if open_browser:
        try:
            webbrowser.open("http://localhost:8080")
        except Exception:
            pass

    # =========================================================================
    # BOUCLE D'ANIMATION SCÉNIQUE RÉALISTE (VU-mètres stéréo 16 pistes & Master)
    # =========================================================================
    t = 0.0
    tick_counter = 0
    try:
        while True:
            t += 0.08
            tick_counter += 1

            if state["is_playing"]:
                # Simulation de pulsation musicale réaliste (Kick 4-on-the-floor, Hi-Hats, Synth swells)
                beat_phase = (t * 2.0) % (2.0 * math.pi)
                kick_pulse = max(0.0, math.cos(beat_phase) ** 4)
                snare_pulse = max(0.0, math.sin(beat_phase * 0.5) ** 6)

                meters = []
                for i in range(16):
                    # Chaque piste a une dynamique rythmique propre
                    if i == 0:  # Drums
                        base = 0.40 + 0.35 * kick_pulse + 0.20 * snare_pulse
                    elif i == 1:  # Bass
                        base = 0.45 + 0.30 * kick_pulse + 0.10 * math.sin(t * 1.5)
                    elif i == 2:  # Pads
                        base = 0.35 + 0.22 * math.sin(t * 0.7 + i)
                    elif i == 8:  # Percs
                        base = 0.30 + 0.40 * (kick_pulse * 0.3 + random.uniform(0.1, 0.4))
                    elif i == 14:  # Synths Group
                        base = 0.40 + 0.25 * math.sin(t * 1.2) + 0.15 * kick_pulse
                    else:
                        base = 0.25 + 0.25 * (math.sin(t * 1.8 + i * 0.9) + 1.0) * 0.5

                    # Variation stéréo L / R
                    l_val = min(1.0, max(0.0, base + random.uniform(-0.04, 0.05)))
                    r_val = min(1.0, max(0.0, base * 0.95 + random.uniform(-0.04, 0.05)))

                    meters.append({
                        "left": round(l_val, 3),
                        "right": round(r_val, 3)
                    })

                server.broadcast({"type": "meters", "data": meters})

                # Animation Master Output (fluctue près de nominal -0.2 dB)
                if tick_counter % 2 == 0:
                    master_pulse = 0.78 + 0.06 * kick_pulse + random.uniform(-0.02, 0.02)
                    server.broadcast({
                        "type": "master_volume",
                        "data": {
                            "value": round(min(0.92, master_pulse), 3),
                            "str": "-0.2 dB"
                        }
                    })

            time.sleep(0.04)  # ~25 FPS réactif

    except KeyboardInterrupt:
        print("\n[INFO] Arrêt propre du simulateur LivePilot 16...")
        server.stop()
        print("[OK] Serveur arrêté. À bientôt !")

if __name__ == "__main__":
    should_open = "--open" in sys.argv
    run_simulator(open_browser=should_open)
