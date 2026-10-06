# LivePilot 16

> **LivePilot 16** is an interactive stage cockpit for Ableton Live, combining 16-track and 24-plugin macro control with real-time, high-visibility visual feedback on tablet.
>
> *(Version française : **LivePilot 16** est un cockpit scénique interactif pour Ableton Live, combinant le contrôle physique de 16 pistes et 24 macros de plugins avec un retour visuel temps réel haute visibilité sur tablette.)*

---

![LivePilot 16 Tablet Cockpit](doc/assets/tablet_cockpit_preview.jpg)

---

## 🌟 Key Features

* **High-Visibility Stage HUD**: Designed specifically for dark stages, festivals, and live performance with high-contrast color coding and zero visual clutter.
* **16-Track Mixer Deck (8x2)**: Direct overview of 16 channels in two rows of 8 tracks, featuring enlarged high-visibility channel banners (numbers & names), dual stereo high-precision linear gradient VU-meters with calibrated 0 dB reference marks, explicit group track differentiation (dashed amber borders & `GRP` badges), real-time dB readouts, and pan indicators. Bank switching allows control over up to 64 tracks (`Bank 1/4`).
* **24 Plugin Macros (8x3)**: 24 rotary encoders with large, high-visibility stage badges numbered `#1` to `#24`, multi-colored LED indicator arcs, clear parameter titles, and numerical values. Dynamic header displays active plugin index and name (`PLUGIN — [2/5] Serum`).
* **3-Card Scene Banner**: Seamless live progression tracking with **Previous Scene**, **Current Scene** (prominent glowing emerald container with play button), and **Next Scene**, free of visual clutter.
* **Direct Track & Device Navigation**: Quick-access touch buttons in the sidebar (`◀ Piste précédente` / `Piste suivante ▶` and `◀ Device précédent` / `Device suivant ▶`) with **Auto-follow device** toggle.
* **Master Output HUD**: Integrated Ableton Master output stereo VU-meter with `MAIN` peak dB monitoring and calibrated scale ticks.
* **Zero Audio Latency**: Native Python 3 MIDI Remote Script communicating with Live's LOM (Live Object Model) and streaming real-time telemetry over WebSockets.
* **Hardware Synergy**: Works seamlessly alongside Novation Launch Control XL (16 track buttons, 24 knobs) and Launchpad Pro MK3 (scene launch, clip trigger).

---

## 📂 Repository Structure

```
LivePilot16/
├── remote_script/LivePilot16/   # [ABLETON] Native Python 3 MIDI Remote Script
│   ├── __init__.py              # Ableton control surface entrypoint
│   ├── LivePilot16.py           # Core LOM listener engine & WebSocket bridge
│   ├── consts.py                # MIDI mappings and default constants
│   ├── web_server.py            # High-performance async WebSocket & HTTP server
│   └── web/                     # Tablet Web App (PWA)
│       ├── index.html           # Cockpit interface structure
│       ├── style.css            # Dark high-contrast stage styling
│       ├── app.js               # Real-time WebSocket telemetry & touch interaction
│       └── logo.png             # Official LivePilot 16 emblem
│
├── doc/                         # [DOCUMENTATION]
│   ├── CAHIER_DES_CHARGES.md    # Full technical & functional specifications
│   ├── GUIDE_TABLETTE_LIVE.md   # Stage tablet setup guide (USB & Wi-Fi)
│   └── assets/                  # High-resolution screenshots and diagrams
│
├── tools/                       # [UTILITIES]
│   ├── install_script.py        # 1-click automatic deployment into Ableton Live
│   └── cockpit_bridge.py        # Standalone testing & simulation server
└── .gitignore                   # Clean ignore rules
```

---

## 🚀 Quick Start

### 1. Install the Remote Script in Ableton Live

Run the automated installer:
```bash
python tools/install_script.py
```

Then in **Ableton Live 11 or 12**:
1. Open `Options` > `Preferences` > `Link, Tempo & MIDI`.
2. Under **Control Surfaces**, select `LivePilot 16`.
3. Set Input and Output to `None` (the script directly hosts the Web/WebSocket server on port `8080`).

### 2. Connect Your Tablet

1. **Option A (Recommended for Stage - USB Cable)**: Connect your tablet to your laptop via USB and enable **USB Tethering** (Modem USB). This provides ultra-low latency, uninterrupted power charging, and immunity to wireless interference.
2. **Option B (Wi-Fi)**: Connect the tablet and laptop to the same Wi-Fi network (or laptop hotspot).
3. Open Chrome, Safari, or Firefox on your tablet and navigate to:
   ```
   http://[YOUR_PC_IP]:8080
   ```
4. Tap **"Add to Home Screen"** to run LivePilot 16 as a borderless full-screen Progressive Web App (PWA).

---

## 📖 Detailed Documentation

* [Cahier des Charges Technique & Fonctionnel](doc/CAHIER_DES_CHARGES.md)
* [Guide Officiel d'Utilisation Tablette en Live](doc/GUIDE_TABLETTE_LIVE.md)

---

## 📜 License

Licensed under the MIT License. Developed for musicians and live performers worldwide.
