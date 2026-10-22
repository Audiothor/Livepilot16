# LivePilot 16 — Constantes de communication MIDI, SysEx & Web Cockpit
# Compatible Ableton Live 11 (Python 3.7) & Ableton Live 12 (Python 3.11)

# En-tête SysEx
SYSEX_START = 0xF0
SYSEX_END = 0xF7
SYSEX_HEADER = (0xF0, 0x00, 0x21, 0x45, 0x10)

# Types de trames (Ableton -> Matériel)
CMD_BANK_INFO     = 0x01
CMD_TRACK_ACTIVE  = 0x02
CMD_BANK_COLORS   = 0x03
CMD_DEVICE_ACTIVE = 0x04
CMD_PARAM_DATA    = 0x05
CMD_SCENE_INFO    = 0x06
CMD_FULL_SYNC_REQ = 0x0F

# Numéros de Control Change (CC) par défaut (Preset LivePilot 16 Novation Components)
CC_BASE_ENCODERS   = 1   # CC 1 à 24 (Knob 1 = CC1, Knob 2 = CC2 ... Knob 24 = CC24)
DEFAULT_KNOB_CCS   = list(range(1, 25))    # CC 1 à 24 (Knobs 1 à 24)
DEFAULT_FADER_CCS  = list(range(25, 33))   # CC 25 à 32 (8 Faders de volume)
DEFAULT_BUTTON_CCS = list(range(33, 49))   # CC 33 à 48 (16 Boutons : Rangée 1 = CC 33..40, Rangée 2 = CC 41..48)
DEFAULT_MIDI_CHANNEL = 1                   # Canal 1 (1-based)

# Preset Novation Launch Control XL Factory (D'usine sans remapping)
FACTORY_KNOB_CCS = [
    13, 14, 15, 16, 17, 18, 19, 20,  # Rangée 1 (Send A) : Knobs 1 à 8
    29, 30, 31, 32, 33, 34, 35, 36,  # Rangée 2 (Send B) : Knobs 9 à 16
    49, 50, 51, 52, 53, 54, 55, 56   # Rangée 3 (Pan)    : Knobs 17 à 24
]
FACTORY_BUTTON_NOTES = [
    41, 42, 43, 44, 45, 46, 47, 48,  # Rangée Focus 1 à 8
    57, 58, 59, 60, 61, 62, 63, 64   # Rangée Control 9 à 16
]

# Mode 16 Factory Template du Launch Control XL (Boutons 1..16 émettent CC 37..52)
LCXL_MODE16_BUTTON_CCS = list(range(37, 53))

# Novation Launch Control XL 3 / Launchkey / DAW Surface Mode Select (CC 30 sur Canal 7 ou tout canal)
CC_NOVATION_MODE_SELECT = 30
# Mapping des codes de modes Novation vers l'index de piste dans la banque (0..15)
NOVATION_MODE_TO_TRACK = {
    1: 0, 6: 0,        # Mode 1 -> Piste 1 (index 0)
    2: 1, 7: 1,        # Mode 2 -> Piste 2 (index 1)
    8: 2,              # Mode 3 -> Piste 3 (index 2)
    9: 3,              # Mode 4 -> Piste 4 (index 3) - "Mode Select Mode 4"
    18: 4, 10: 4,      # Mode 5 -> Piste 5 (index 4)
    19: 5, 11: 5,      # Mode 6 -> Piste 6 (index 5)
    20: 6, 12: 6,      # Mode 7 -> Piste 7 (index 6)
    21: 7, 13: 7,      # Mode 8 -> Piste 8 (index 7)
    22: 8, 14: 8,      # Mode 9 -> Piste 9 (index 8)
    23: 9, 15: 9,      # Mode 10 -> Piste 10 (index 9)
    24: 10, 16: 10,    # Mode 11 -> Piste 11 (index 10)
    25: 11,            # Mode 12 -> Piste 12 (index 11)
    26: 12,            # Mode 13 -> Piste 13 (index 12)
    27: 13,            # Mode 14 -> Piste 14 (index 13)
    28: 14,            # Mode 15 -> Piste 15 (index 14)
    29: 15,            # Mode 16 -> Piste 16 (index 15)
}

# Handshake DAW Mode Novation Launch Control XL 3 (Programmer's Reference Guide Version 1.0)
NOVATION_DAW_MODE_ON_SYSEX = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x02, 0x7F, 0xF7)
NOVATION_DAW_MODE_OFF_SYSEX = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x02, 0x00, 0xF7)
NOVATION_DAW_MODE_ON_NOTE = (0x9F, 0x0C, 0x7F)
NOVATION_DAW_MODE_OFF_NOTE = (0x9F, 0x0C, 0x00)
NOVATION_FEATURE_CONTROLS_ON_NOTE = (0x9F, 0x0B, 0x7F)
NOVATION_FEATURE_CONTROLS_OFF_NOTE = (0x9F, 0x0B, 0x00)

# Sélection du mode de surface DAW (Guide Développeur Page 10 & 17 : B6h 1Eh <mode>)
# 01h = DAW Mixer, 02h = DAW Control (active Page ▲/▼, Track ◄/►, 16 Pads, 24 Knobs, 8 Faders et toutes les LEDs)
NOVATION_SURFACE_DAW_MIXER = (0xB6, 0x1E, 0x01)
NOVATION_SURFACE_DAW_CONTROL = (0xB6, 0x1E, 0x02)

# Forcer les 3 rangées d'encodeurs en mode Absolu 0..127 (Guide Développeur Page 10)
NOVATION_ENCODER_ROW1_ABS = (0xB6, 0x45, 0x00)
NOVATION_ENCODER_ROW2_ABS = (0xB6, 0x48, 0x00)
NOVATION_ENCODER_ROW3_ABS = (0xB6, 0x49, 0x00)

# Configuration par défaut des 4 boutons de navigation matériels (Page ▲/▼ et Track ◄/►)
DEFAULT_NAV_BUTTONS = {
    'page_up':     {'cc': 106, 'type': 'cc', 'channel': 1, 'action': 'bank_prev'},
    'page_down':   {'cc': 107, 'type': 'cc', 'channel': 1, 'action': 'bank_next'},
    'track_left':  {'cc': 103, 'type': 'cc', 'channel': 1, 'action': 'track_prev'},
    'track_right': {'cc': 102, 'type': 'cc', 'channel': 1, 'action': 'track_next'}
}

# Indices matériels officiels des 16 boutons (Guide Développeur Page 9)
# Rangée 1 (Pistes 1..8) : 37..44 (25h..2Ch)
# Rangée 2 (Pistes 9..16): 45..52 (2Dh..34h)
LCXL3_BUTTON_INDICES = [
    37, 38, 39, 40, 41, 42, 43, 44,
    45, 46, 47, 48, 49, 50, 51, 52
]
LCXL3_RGB_SYSEX_HEADER = (0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x01, 0x53)

# En mode DAW Novation (Indices officiels du Programmer's Reference Guide)
DAW_FADER_CCS = list(range(5, 13))    # CC 5 à 12 (8 faders sur canal 16)
DAW_KNOB_CCS = list(range(13, 37))    # CC 13 à 36 (24 knobs sur canal 16)
DAW_BUTTON_CCS = list(range(37, 53))  # CC 37 à 52 (16 pads sur canal 1)

# Boutons matériels supplémentaires Launch Control XL 3 (DAW Mode)
CC_HW_PLAY         = 116  # Bouton Play matériel
CC_HW_RECORD       = 118  # Bouton Record matériel
CC_HW_SOLO_ARM     = 65   # Bouton Solo/Arm matériel
CC_HW_MUTE_SELECT  = 66   # Bouton Mute/Select matériel
CC_HW_CLIP_STOP    = 104  # Bouton Clip Stop matériel

# CC Virtuels Jog / Poussoir Master
CC_ENC17_JOG       = 109  # CC 109 (Master Jog / BPM virtuel)
CC_ENC17_PUSH      = 110  # CC 110 (Clic poussoir Master virtuel)

# Boutons de Navigation Système
CC_NAV_LEFT        = 54  # Flèche Gauche ◄
CC_NAV_RIGHT       = 55  # Flèche Droite ►
CC_BTN_VALID       = 56  # Bouton de validation [VALID]
CC_NAV_GROUP_PREV  = 58  # Group < (Groupe précédent)
CC_NAV_GROUP_NEXT  = 59  # Group > (Groupe suivant)
CC_NAV_TRACK_PREV  = 60  # Track < (Banque précédente fallback)
CC_NAV_TRACK_NEXT  = 61  # Track > (Banque suivante fallback)
CC_NAV_DEV_PREV    = 62  # Device < (Device précédent)
CC_NAV_DEV_NEXT    = 63  # Device > (Device suivant)

# Boutons de Navigation Matérielle Launch Control XL / Launch Control XL 3
CC_NAV_TRACK_LEFT   = 103  # Track ◄ (Piste précédente)
CC_NAV_TRACK_RIGHT  = 102  # Track ► (Piste suivante)
CC_NAV_PAGE_UP      = 106  # Page ▲ (Banque précédente)
CC_NAV_PAGE_DOWN    = 107  # Page ▼ (Banque suivante)

# 16 Boutons de Sélection de Piste du Launch Control XL (Mode CC alternatif)
CC_BASE_TRACK_SEL  = 64  # CC 64 à 79 (Boutons 1 à 16)

# Configuration de taille adaptée au Setup Live (Launch Control XL + Launchpad Pro MK3 + Tablette)
NUM_TRACKS_PER_BANK = 16  # 16 pistes (correspondant aux 16 boutons du Launch Control XL)
NUM_ENCODERS = 24         # 24 potentiomètres (3 rangées de 8 knobs du Launch Control XL)
DEFAULT_HTTP_PORT = 8080  # Port HTTP / WebSocket pour la tablette Android
