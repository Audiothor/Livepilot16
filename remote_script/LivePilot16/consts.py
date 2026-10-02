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

# Numéros de Control Change (CC)
CC_BASE_ENCODERS   = 16  # CC 16 à 39 (jusqu'à 24 encodeurs)
CC_ENC17_JOG       = 32  # CC 32 (Encodeur Master : BPM Live / Paramètre / Jog)
CC_ENC17_PUSH      = 33  # CC 33 (Clic poussoir Master)

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

CC_BASE_TRACK_SEL  = 64  # CC 64 à 71 (Boutons Piste 1 à 8)

# Configuration de taille adaptée au Setup Live (Launch Control XL + Launchpad Pro MK3 + Tablette)
NUM_TRACKS_PER_BANK = 8   # 8 pistes par tranche (miroir 1:1 du Launch Control XL et Launchpad)
NUM_ENCODERS = 24         # 24 encodeurs (3 rangées de 8 knobs du Launch Control XL)
DEFAULT_HTTP_PORT = 8080  # Port HTTP / WebSocket pour la tablette Android
