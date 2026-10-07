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

# Numéros de Control Change (CC) par défaut (Preset LivePilot : CC 1..24 & CC 25..40)
CC_BASE_ENCODERS   = 1   # CC 1 à 24 (Knob 1 = CC1, Knob 2 = CC2 ... Knob 24 = CC24)
DEFAULT_KNOB_CCS   = list(range(1, 25))    # CC 1 à 24
DEFAULT_BUTTON_CCS = list(range(25, 41))   # CC 25 à 40 (16 boutons sous faders)
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

CC_ENC17_JOG       = 40  # CC 40 (Master Jog / BPM)
CC_ENC17_PUSH      = 41  # CC 41 (Clic poussoir Master)

# Boutons de Navigation Système
CC_NAV_LEFT        = 54  # Flèche Gauche ◄
CC_NAV_RIGHT       = 55  # Flèche Droite ►
CC_BTN_VALID       = 56  # Bouton de validation [VALID]
CC_NAV_GROUP_PREV  = 58  # Group < (Groupe précédent)
CC_NAV_GROUP_NEXT  = 59  # Group > (Groupe suivant)
CC_NAV_TRACK_PREV  = 60  # Track < (Banque précédente)
CC_NAV_TRACK_NEXT  = 61  # Track > (Banque suivante)
CC_NAV_DEV_PREV    = 62  # Device < (Device précédent)
CC_NAV_DEV_NEXT    = 63  # Device > (Device suivant)

# 16 Boutons de Sélection de Piste du Launch Control XL (Mode CC alternatif)
CC_BASE_TRACK_SEL  = 64  # CC 64 à 79 (Boutons 1 à 16)

# Configuration de taille adaptée au Setup Live (Launch Control XL + Launchpad Pro MK3 + Tablette)
NUM_TRACKS_PER_BANK = 16  # 16 pistes (correspondant aux 16 boutons du Launch Control XL)
NUM_ENCODERS = 24         # 24 potentiomètres (3 rangées de 8 knobs du Launch Control XL)
DEFAULT_HTTP_PORT = 8080  # Port HTTP / WebSocket pour la tablette Android
