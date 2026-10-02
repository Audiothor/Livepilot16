#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LivePilot Cockpit — Simulateur / Serveur de test autonome
Permet de visualiser l'interface sur la tablette Android et de tester
le rendu des VU-mètres, des knobs et des scènes même sans ouvrir Ableton Live.
"""

import os
import sys
import time
import math
import random
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remote_script", "LivePilot16")))
from web_server import LivePilotWebServer

def run_simulator():
    web_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remote_script", "LivePilot16", "web"))
    
    server = LivePilotWebServer(port=8080, web_dir=web_dir)
    if not server.start():
        print("[ERREUR] Impossible de lancer le serveur sur le port 8080.")
        return

    ips = server.get_local_ips()
    print("=" * 65)
    print("  LIVEPILOT COCKPIT — SERVEUR DE TEST AUTONOME ACTIF")
    print("=" * 65)
    print("Ouvrez votre tablette Android (Chrome ou Firefox) à l'adresse :")
    for ip in ips:
        print(f"  -> http://{ip}:{server.port}")
    print("Ou sur ce PC :")
    print(f"  -> http://localhost:{server.port}")
    print("-" * 65)
    print("Appuyez sur Ctrl+C pour quitter.")
    print("=" * 65)

    # Données simulées
    demo_tracks = [
        {"index": 0, "name": "Kick & Bass", "color": "#ff3355", "is_group": True, "mute": False, "solo": False, "arm": False, "vol_str": "-2.1 dB", "pan_str": "C"},
        {"index": 1, "name": "Snare Clap", "color": "#ff9900", "is_group": False, "mute": False, "solo": False, "arm": False, "vol_str": "-4.0 dB", "pan_str": "12L"},
        {"index": 2, "name": "HiHats 909", "color": "#ffcc00", "is_group": False, "mute": False, "solo": False, "arm": False, "vol_str": "-6.5 dB", "pan_str": "15R"},
        {"index": 3, "name": "Percs Loop", "color": "#00ff88", "is_group": False, "mute": False, "solo": False, "arm": False, "vol_str": "-8.2 dB", "pan_str": "C"},
        {"index": 4, "name": "Acid Synth 303", "color": "#00f0ff", "is_group": False, "mute": False, "solo": False, "arm": True, "vol_str": "-1.5 dB", "pan_str": "5L"},
        {"index": 5, "name": "Poly Pad Atmos", "color": "#3a86ff", "is_group": False, "mute": False, "solo": False, "arm": False, "vol_str": "-7.0 dB", "pan_str": "C"},
        {"index": 6, "name": "Vocal Chopped", "color": "#8338ec", "is_group": False, "mute": False, "solo": False, "arm": False, "vol_str": "-3.8 dB", "pan_str": "8R"},
        {"index": 7, "name": "Reverb Master", "color": "#ff007f", "is_group": False, "mute": False, "solo": False, "arm": False, "vol_str": "-12.0 dB", "pan_str": "C"},
    ]

    demo_scenes = [
        {"index": 0, "name": "01 - INTRO", "color": "#3a86ff", "is_playing": False},
        {"index": 1, "name": "02 - BUILD UP", "color": "#ff9900", "is_playing": False},
        {"index": 2, "name": "03 - MAIN DROP", "color": "#00ff88", "is_playing": True},
        {"index": 3, "name": "04 - BREAKDOWN", "color": "#8338ec", "is_playing": False},
        {"index": 4, "name": "05 - DROP 2 ACID", "color": "#ff0055", "is_playing": False},
        {"index": 5, "name": "06 - OUTRO", "color": "#555555", "is_playing": False},
    ]

    demo_params = [
        {"index": 0, "name": "Cutoff", "value": 0.65, "str": "2.40 kHz"},
        {"index": 1, "name": "Resonance", "value": 0.45, "str": "45 %"},
        {"index": 2, "name": "Drive", "value": 0.30, "str": "+4.5 dB"},
        {"index": 3, "name": "Sub Level", "value": 0.80, "str": "-1.2 dB"},
        {"index": 4, "name": "Morph", "value": 0.50, "str": "50 %"},
        {"index": 5, "name": "Attack", "value": 0.05, "str": "12 ms"},
        {"index": 6, "name": "Decay", "value": 0.40, "str": "420 ms"},
        {"index": 7, "name": "Env Mod", "value": 0.70, "str": "+70 %"},
        {"index": 8, "name": "Delay Time", "value": 0.33, "str": "3/16 D"},
        {"index": 9, "name": "Feedback", "value": 0.55, "str": "55 %"},
        {"index": 10, "name": "Reverb Dry", "value": 0.25, "str": "25 %"},
        {"index": 11, "name": "Chor Depth", "value": 0.40, "str": "40 %"},
        {"index": 12, "name": "Compress Th", "value": 0.60, "str": "-18 dB"},
        {"index": 13, "name": "Ratio", "value": 0.50, "str": "4:1"},
        {"index": 14, "name": "Sidechain", "value": 0.75, "str": "75 %"},
        {"index": 15, "name": "Makeup", "value": 0.35, "str": "+3.5 dB"},
        {"index": 16, "name": "LFO 1 Rate", "value": 0.50, "str": "1/4"},
        {"index": 17, "name": "LFO 1 Amt", "value": 0.60, "str": "60 %"},
        {"index": 18, "name": "LFO 2 Shape", "value": 0.20, "str": "Sine"},
        {"index": 19, "name": "Glide", "value": 0.15, "str": "35 ms"},
        {"index": 20, "name": "Spread", "value": 0.85, "str": "85 %"},
        {"index": 21, "name": "High Cut", "value": 0.90, "str": "16 kHz"},
        {"index": 22, "name": "Low Cut", "value": 0.10, "str": "30 Hz"},
        {"index": 23, "name": "Master Vol", "value": 0.78, "str": "-0.5 dB"},
    ]

    def on_message(msg):
        action = msg.get("action")
        if action == "request_full_sync":
            server.broadcast({
                "type": "full_sync",
                "data": {
                    "tempo": 126.0,
                    "is_playing": True,
                    "position": "17.2.1",
                    "active_scene": {"name": "03 - MAIN DROP", "color": "#00ff88"},
                    "scenes": demo_scenes,
                    "bank_index": 0,
                    "total_banks": 2,
                    "selected_track_index": 4,
                    "tracks": demo_tracks,
                    "devices": [{"name": "Wavetable"}, {"name": "Auto Filter"}, {"name": "Echo"}, {"name": "Glue Comp"}],
                    "active_device_index": 1,
                    "active_device_name": "Auto Filter (Acid Mod)",
                    "parameters": demo_params
                }
            })
        elif action == "select_track":
            t_idx = msg.get("track_index", 0)
            server.broadcast({
                "type": "track_selected",
                "data": {
                    "track_index": t_idx,
                    "tracks": demo_tracks,
                    "devices": [{"name": "Device 1"}, {"name": "Device 2"}],
                    "active_device_name": f"Device on Track {t_idx+1}",
                    "active_device_index": 0,
                    "parameters": demo_params
                }
            })

    server.on_client_message = on_message

    # Boucle d'animation des VU-mètres pour le test
    t = 0
    try:
        while True:
            t += 0.1
            meters = []
            for i in range(8):
                base = (math.sin(t * 2 + i * 0.8) + 1.0) * 0.4
                rand_val = random.uniform(0.0, 0.15)
                val_l = min(1.0, max(0.0, base + rand_val))
                val_r = min(1.0, max(0.0, base + rand_val * 0.8))
                meters.append({"left": round(val_l, 3), "right": round(r, 3) if 'r' in locals() else round(val_r, 3)})
            server.broadcast({"type": "meters", "data": meters})
            time.sleep(0.04)
    except KeyboardInterrupt:
        print("\nArrêt du serveur simulateur...")
        server.stop()

if __name__ == "__main__":
    run_simulator()
