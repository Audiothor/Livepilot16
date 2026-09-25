#pragma once
#include <Arduino.h>

/**
 * ============================================================================
 * LivePilot 16 — Configuration Matérielle & Broches ESP32-S3
 * ============================================================================
 */

// --- Bus I2C pour les 4 MCP23017 ---
#define I2C_SDA_PIN             8
#define I2C_SCL_PIN             9
#define I2C_FREQ_HZ             400000   // Fast Mode 400kHz

// Broches d'interruption matérielle des MCP23017
#define MCP_INTA_PIN            4
#define MCP_INTB_PIN            5

// Adresses I2C des 4 MCP23017 (A0, A1, A2 configurés sur le PCB)
#define MCP_ADDR_ENC_1_8        0x20     // Encodeurs 1 à 8 (Phases A & B)
#define MCP_ADDR_ENC_9_16       0x21     // Encodeurs 9 à 16 (Phases A & B)
#define MCP_ADDR_BTNS_TRACKS    0x22     // 16 Boutons de sélection de piste
#define MCP_ADDR_BTNS_NAV_PUSH  0x23     // 4 Boutons Nav + Poussoirs d'encodeurs

// --- Bus SPI Partagé pour Double Écran TFT ILI9488 (2x 480x320 = 960x320 px) ---
#define TFT_MOSI_PIN            11       // Données SPI partagées
#define TFT_SCLK_PIN            12       // Horloge SPI partagée (40 MHz)
#define TFT_DC_PIN              13       // Data / Command partagé
#define TFT_RST_PIN             14       // Reset matériel partagé
#define TFT_BL_PIN              21       // Rétroéclairage PWM partagé
#define TFT_CS_LEFT_PIN         10       // Chip Select Écran Gauche (Vue Mix & Session)
#define TFT_CS_RIGHT_PIN        38       // Chip Select Écran Droit (Vue Plugins & Paramètres)

// --- Ruban de LEDs RGB (16x WS2812B-Mini) ---
#define RGB_LEDS_DATA_PIN       48       // Broche RMT pour LEDs RGB
#define NUM_RGB_LEDS            16

// --- 6 Boutons de Navigation (GPIO directs ESP32-S3 avec pull-up interne) ---
#define PIN_NAV_TRACK_PREV      15       // Track - (Banque précédente)
#define PIN_NAV_TRACK_NEXT      16       // Track + (Banque suivante)
#define PIN_NAV_GROUP_PREV      17       // Group - (Groupe précédent)
#define PIN_NAV_GROUP_NEXT      18       // Group + (Groupe suivant)
#define PIN_NAV_DEV_PREV        1        // Device - (Device précédent)
#define PIN_NAV_DEV_NEXT        2        // Device + (Device suivant)

// Constantes d'interface
#define NUM_ENCODERS            16
#define NUM_TRACK_BUTTONS       16
#define NUM_NAV_BUTTONS         6        // TRACK -/+, GROUP -/+, DEVICE -/+
