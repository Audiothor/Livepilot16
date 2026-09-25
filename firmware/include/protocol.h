#pragma once
#include <Arduino.h>

/**
 * ============================================================================
 * LivePilot 16 — Protocole de Communication MIDI & SysEx
 * ============================================================================
 */

// SysEx Fabricant / Modèle (ID non-commercial 0x7D ou réservé 0x00 0x21 0x45)
#define SYSEX_START             0xF0
#define SYSEX_END               0xF7
#define SYSEX_MANUF_ID_0        0x00
#define SYSEX_MANUF_ID_1        0x21
#define SYSEX_MANUF_ID_2        0x45
#define SYSEX_DEVICE_ID         0x10     // LivePilot 16 ID

// Types de trames SysEx (Ableton Live -> LivePilot 16)
enum SysExCommand : uint8_t {
    CMD_BANK_INFO       = 0x01,  // Banque active (index, total de banques, nb pistes)
    CMD_TRACK_ACTIVE    = 0x02,  // Piste active (numéro, flag_assignation: 1/0, is_group: 1/0, nom UTF-8)
    CMD_BANK_COLORS     = 0x03,  // Palette des 16 pistes (RGB; Blanc pur si piste sélectionnée sans assignation)
    CMD_DEVICE_ACTIVE   = 0x04,  // Plugin actif (index, total_assignes, nav_active: 1/0, nom UTF-8)
    CMD_PARAM_DATA      = 0x05,  // Paramètre (index 0-15, nom, valeur textuelle, valeur 0-127)
    CMD_FULL_SYNC_REQ   = 0x0F   // Demande de synchronisation complète
};

// Plage des numéros de Control Change (CC)
#define CC_BASE_ENCODERS        16       // CC 16 à 31 pour les 16 encodeurs (relatifs)
#define CC_BASE_NAV_GROUP_PREV  58       // CC 58: Group < (Groupe précédent)
#define CC_BASE_NAV_GROUP_NEXT  59       // CC 59: Group > (Groupe suivant)
#define CC_BASE_NAV_TRACK_PREV  60       // CC 60: Track < (Banque précédente)
#define CC_BASE_NAV_TRACK_NEXT  61       // CC 61: Track > (Banque suivante)
#define CC_BASE_NAV_DEV_PREV    62       // CC 62: Dev < (Device assigné précédent - actif si > 1)
#define CC_BASE_NAV_DEV_NEXT    63       // CC 63: Dev > (Device assigné suivant - actif si > 1)
#define CC_BASE_TRACK_SEL       64       // CC 64 à 79: Sélection directe de piste 1 à 16

// Mode d'encodage relatif des encodeurs (Signed Bit)
inline int8_t decodeRelativeCC(uint8_t value) {
    if (value & 0x40) {
        return -(int8_t)(value & 0x3F);
    } else {
        return (int8_t)(value & 0x3F);
    }
}

inline uint8_t encodeRelativeCC(int8_t step) {
    if (step < 0) {
        return 0x40 | ((-step) & 0x3F);
    } else {
        return step & 0x3F;
    }
}
