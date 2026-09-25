# LivePilot 16 — Constantes de communication MIDI & SysEx
# Compatible Ableton Live 11 (Python 3.7) & Ableton Live 12 (Python 3.11)

# En-tête SysEx
SYSEX_START = 0xF0
SYSEX_END = 0xF7
SYSEX_HEADER = (0xF0, 0x00, 0x21, 0x45, 0x10)

# Types de trames (Ableton -> ESP32-S3)
CMD_BANK_INFO     = 0x01
CMD_TRACK_ACTIVE  = 0x02
CMD_BANK_COLORS   = 0x03
CMD_DEVICE_ACTIVE = 0x04
CMD_PARAM_DATA    = 0x05
CMD_SCENE_INFO    = 0x06
CMD_FULL_SYNC_REQ = 0x0F

# Numéros de Control Change (CC)
CC_BASE_ENCODERS   = 16  # CC 16 à 31 (16 encodeurs relatifs)

# Boutons de Navigation (6 boutons : TRACK, GROUP, DEVICE)
CC_NAV_GROUP_PREV  = 58  # Group < (Groupe précédent)
CC_NAV_GROUP_NEXT  = 59  # Group > (Groupe suivant)
CC_NAV_TRACK_PREV  = 60  # Track < (Banque précédente)
CC_NAV_TRACK_NEXT  = 61  # Track > (Banque suivante)
CC_NAV_DEV_PREV    = 62  # Device < (Device précédent)
CC_NAV_DEV_NEXT    = 63  # Device > (Device suivant)

CC_BASE_TRACK_SEL  = 64  # CC 64 à 79 (Boutons Piste 1 à 16)

# Configuration de taille
NUM_TRACKS_PER_BANK = 16
NUM_ENCODERS = 16
NUM_NAV_BUTTONS = 6
