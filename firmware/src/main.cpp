/**
 * ============================================================================
 * LivePilot 16 — Firmware Principal ESP32-S3
 * Surface de Contrôle Dédiée à Ableton Live
 * Slogan : "Ne regardez plus l'écran, pilotez votre son."
 * ============================================================================
 */

#include <Arduino.h>
#include <Wire.h>
#include "config.h"
#include "protocol.h"

// Déclaration des tâches FreeRTOS (Dual-Core)
TaskHandle_t taskCore0_IO_Handle = NULL;
TaskHandle_t taskCore1_UI_Handle = NULL;

// Structure d'état globale du contrôleur
struct LivePilotState {
    // Gestion des banques
    uint8_t currentBankIndex = 0;
    uint8_t totalBanks = 1;
    uint8_t totalTracks = 0;
    
    // Piste active & règle d'assignation
    uint8_t selectedTrackIndex = 0;
    bool isGroupTrack = false;        // Piste de groupe Ableton (is_foldable)
    bool trackHasAssignments = false; // RÈGLE : Si false, bouton sélectionné = BLANC PUR
    char selectedTrackName[32] = "No Track";
    uint8_t selectedTrackColor[3] = {255, 255, 255}; // Blanc par défaut si non assignée
    
    // Scène en cours & Tempo Ableton Live
    uint8_t currentSceneIndex = 0;
    bool isScenePlaying = false;
    float currentTempo = 120.0f;
    char currentSceneName[128] = "Scene 1"; // Nom étendu à 128 chars pour longues indications scéniques
    uint16_t sceneScrollOffset = 0;         // Offset pour défilement horizontal fluide (Marquee Ticker)
    uint8_t currentSceneColor[3] = {60, 160, 240}; // Couleur exacte de la scène dans Ableton
    
    // Device actif & règle de navigation
    uint8_t selectedDeviceIndex = 0;
    uint8_t totalAssignedDevices = 0;  // Nombre de devices avec assignations
    bool deviceNavEnabled = false;     // RÈGLE : Actif UNIQUEMENT si totalAssignedDevices > 1
    char selectedDeviceName[32] = "No Assignment";
    
    // 16 Paramètres de l'encodeur
    struct ParameterInfo {
        char name[16] = "---";
        char valueStr[16] = "--";
        uint8_t rawValue = 0;
        bool active = false;
    } params[NUM_ENCODERS];
    
    // Couleurs RGB des 16 touches de pistes
    uint8_t bankTrackColors[NUM_TRACK_BUTTONS][3];
    
    // Drapeaux de rafraîchissement
    bool needsDisplayRedraw = true;
    bool needsLedUpdate = true;
} state;

// Tâche Core 0 : Acquisition ultra-rapide des interruptions I2C & MIDI USB
void TaskCore0_IO(void *pvParameters) {
    Serial.println("[Core 0] Tâche I/O et Décodage Encodeurs démarrée.");
    
    for (;;) {
        // 1. Scrutation / interruption des MCP23017
        // 2. Détection de changement d'état des 16 encodeurs de paramètres (Gray Code)
        // 3. Détection directe du 17ᵉ Encodeur Master (GPIO 40/41, Jog/Tempo) & clic poussoir (GPIO 39)
        // 4. Détection d'appui sur le bouton de validation [VALID] (GPIO 42, CC 56)
        // 5. Détection d'appui sur les 16 touches de pistes (CC 64..79)
        // 6. Détection des 8 boutons de navigation (Colonne 4×2 à droite) :
        //    - Rangée 1 : Flèches ◄ / ► (GPIO 6 / 7, CC 54 / 55) : navigation scènes / pages
        //    - Rangée 2 : GROUP - / GROUP + (GPIO 17 / 18, CC 58 / 59) : saut direct de groupe en groupe
        //    - Rangée 3 : DEVICE - / DEVICE + (GPIO 1 / 2, CC 62 / 63, conditionné par state.deviceNavEnabled)
        //    - Rangée 4 : TRACK - / TRACK + (GPIO 15 / 16, CC 60 / 61) : pagination banques de 16 pistes
        // 7. Émission immédiate des messages MIDI CC vers Ableton
        
        vTaskDelay(pdMS_TO_TICKS(1)); // Cycle 1ms pour latence imperceptible
    }
}

// Tâche Core 1 : Moteur graphique Double Écran TFT (LovyanGFX), UI et animation LEDs RGB
void TaskCore1_UI(void *pvParameters) {
    Serial.println("[Core 1] Tâche Rendu Graphique Double TFT (960x320) et LEDs démarrée.");
    
    for (;;) {
        // 1. Parsing des trames SysEx entrantes depuis Ableton :
        //    - CMD_TRACK_ACTIVE : maj state.trackHasAssignments, state.isGroupTrack
        //    - CMD_SCENE_INFO   : maj state.currentSceneName, state.currentSceneColor, state.isScenePlaying, state.currentTempo
        //    - CMD_DEVICE_ACTIVE : maj state.totalAssignedDevices et state.deviceNavEnabled
        //    - CMD_BANK_COLORS : si piste sélectionnée sans assignation, couleur = Blanc pur
        //    - CMD_PARAM_DATA : maj des 16 valeurs/noms de paramètres
        
        // 2. Rendu Écran Gauche (Vue Mix & Session - CS GPIO 10, 480x320) :
        //    - Ligne 1 (Y: 0..26) : [BANK 02] à gauche, 126.0 BPM à droite (pas de label superflu "SESSION")
        //    - Ligne 2 (Y: 28..58) : BANDEAU SCÈNE PLEINE LARGEUR (Fond couleur Ableton) :
        //      * Support des textes longs : Défilement horizontal automatique fluide (Marquee text ticker)
        //        si le libellé dépasse la largeur d'écran, permettant de lire l'intégralité des annotations scéniques !
        //    - Zone Pistes (Y: 62..318) : 2 GRANDES COLONNES VERTICALES DE 8 PISTES (Lisibilité maximale 16-20 caractères) :
        //      * Colonne Gauche (X: 2..238) : Pistes 01 à 08 (correspondant 1:1 à la Rangée Haute des pads 1-8)
        //      * Colonne Droite (X: 242..478) : Pistes 09 à 16 (correspondant 1:1 à la Rangée Basse des pads 9-16)
        //      * Largeur de 236 px par piste : affiche le nom complet en toutes lettres sans tronquer !
        //      * Badge [📁] pour les GROUPES et surbrillance blanche néon unique pour la piste active (ex: ▶05: BASS SYNTH GRP)
        
        // 3. Rendu Écran Droit (Vue Plugins & 16 Paramètres - CS GPIO 38) :
        //    - En-tête : Affichage direct et épuré "[D02/03] Glue Compressor" (sans le texte redondant "ACTIVE DEVICE :")
        //    - Matrice 2x8 des 16 paramètres des encodeurs (jauges rotatives, valeurs, labels)
        //    - Si !state.trackHasAssignments : affiche l'état "NO ASSIGNMENT" en plein écran
        //    - Mise à jour ultra-rapide et indépendante lors de la manipulation des encodeurs
        
        // 4. Actualisation des 16 LEDs RGB (WS2812B) :
        //    - Piste sélectionnée sans assignation -> Blanc pur (255, 255, 255)
        //    - Piste sélectionnée avec assignation -> Couleur Ableton à 100% + breathing
        //    - Piste non sélectionnée -> Couleur Ableton tamisée (30%)
        
        // 5. Actualisation des 8 boutons de navigation :
        //    - DEVICE - / DEVICE + allumés si state.deviceNavEnabled, sinon éteints
        //    - GROUP - / GROUP + allumés si des groupes existent dans le projet
        
        vTaskDelay(pdMS_TO_TICKS(16)); // ~60 Hz de rafraîchissement d'interface
    }
}

void setup() {
    Serial.begin(115200);
    delay(500);
    Serial.println("==========================================");
    Serial.println("   LivePilot 16 — Initialisation Firmware  ");
    Serial.println("   Ne regardez plus l'ecran, pilotez !    ");
    Serial.println("==========================================");

    // Initialisation du bus I2C pour les 4 MCP23017
    Wire.begin(I2C_SDA_PIN, I2C_SCL_PIN, I2C_FREQ_HZ);

    // Création des tâches FreeRTOS sur les 2 cœurs physiques de l'ESP32-S3
    xTaskCreatePinnedToCore(
        TaskCore0_IO,
        "Task_IO",
        8192,
        NULL,
        2, // Haute priorité pour l'I/O
        &taskCore0_IO_Handle,
        0  // Core 0
    );

    xTaskCreatePinnedToCore(
        TaskCore1_UI,
        "Task_UI",
        16384,
        NULL,
        1, // Priorité normale pour l'écran
        &taskCore1_UI_Handle,
        1  // Core 1
    );
}

void loop() {
    // La boucle principale loop() est déléguée aux tâches FreeRTOS Core 0 et Core 1
    vTaskDelay(pdMS_TO_TICKS(1000));
}
