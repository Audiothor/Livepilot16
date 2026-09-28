# LivePilot 16 — Guide d'Assemblage Débutant & Options de Fabrication

> **"Même sans expérience en électronique, ce contrôleur est conçu pour être assemblé facilement et sans stress."**

---

## 1. Deux Façons de Construire votre LivePilot 16

| Critère | Option A : Clé en Main SMT (Recommandée débutant) | Option B : Soudure Manuelle DIY (Apprentissage) |
|---|---|---|
| **Niveau de difficulté** | **1 / 5** (Niveau Lego / Meuble IKEA) | **2.5 / 5** (Accessible à toute personne motivée) |
| **Soudure nécessaire** | **0% de soudure complexe** (faite en usine) | Soudures traversantes simples (pas de 2.54 mm) |
| **Temps d'assemblage** | **45 minutes** (vissage + branchement) | **2 à 3 heures** au fer à souder |
| **Matériel requis** | 1 tournevis cruciforme + 1 clé plate | 1 fer à souder 25W (20 €) + étain + tournevis |
| **Surcoût usine** | ~20 € à 30 € pour faire fabriquer la carte soudée | 0 € (vos composants achetés bruts) |

---

## 2. Option A : L'Option "Zéro Soudure" via JLCPCB SMT (La Solution Sérénité)

En 2026, faire fabriquer un circuit imprimé ne signifie plus souder des dizaines de puces à la main. Les fabricants de PCB comme **JLCPCB** ou **PCBWay** disposent de machines de placement automatisé (Pick & Place) :

1. **Vous envoyez les 3 fichiers fournis dans le dossier `hardware/`** :
   * Les fichiers de routage (**Gerber**).
   * La liste des pièces (**BOM**).
   * Le fichier de coordonnées des composants (**CPL / Centroid**).
2. **L'usine soude automatiquement à 100%** :
   * Les résistances de pull-up I2C et protections USB.
   * Les 4 circuits expandeurs MCP23017.
   * Les 16 LEDs RGB NeoPixel WS2812B.
   * Les connecteurs et barrettes femelles réceptrices.
3. **Ce que vous recevez chez vous** :
   * Une carte électronique finie, inspectée aux rayons X et testée électriquement.
4. **Votre montage final à la maison (45 min chrono)** :
   * **Étape 1** : Enficher le module ESP32-S3 sur ses barrettes (comme une cartouche de console).
   * **Étape 2** : Brancher les 2 nappes d'écrans TFT sur leurs connecteurs à détrompeur.
   * **Étape 3** : Insérer les encodeurs rotatifs dans la façade et serrer les écrous de façade.
   * **Étape 4** : Poser la membrane silicone des touches, placer le fond et visser les 4 vis du boîtier.

---

## 3. Option B : La Soudure Manuelle DIY (Pour le plaisir de fabriquer soi-même)

Si vous souhaitez souder vous-même votre contrôleur, sachez que **l'architecture du LivePilot 16 a été spécialement conçue pour éviter tout composant difficile** :

### Pourquoi c'est très facile même pour un débutant :
1. **Zéro composant microscopique CMS (Surface Mount)** :
   * Tous les composants manuels sont au format **Traversant (THT / Through-Hole)**. Leurs broches traversent de larges trous métallisés espacés de **2,54 mm**.
2. **Supports tulipes pour les circuits intégrés** :
   * Vous ne soudez jamais directement les 4 puces MCP23017 ! Vous soudez uniquement des supports en plastique vides. Une fois les soudures refroidies, vous insérez délicatement les puces dedans. Zéro risque de griller un composant par surchauffe.
3. **Le cœur ESP32-S3 est déjà pré-assemblé** :
   * Le microcontrôleur n'est pas une puce nue : c'est un module officiel `ESP32-S3-DevKitC-1` qui intègre déjà le port USB-C, le régulateur de tension et les mémoires Flash/PSRAM. Vous ne faites que l'enficher.
4. **Sérigraphie ultra-pédagogique sur le circuit imprimé** :
   * Tout est écrit en clair sur la carte en blanc : les numéros d'encodeurs (`ENC01` à `ENC16`), la polarité des condensateurs, les numéros de GPIO (`GPIO 10`, `SDA`, `SCL`...). Impossible de se tromper d'emplacement.

---

## 4. Les Filets de Sécurité Intégrés au Projet

Pour que votre montage soit infaillible, nous avons intégré plusieurs protections logicielles et matérielles :

1. **Auto-Diagnostic Série USB au Démarrage** :
   * Dès que vous branchez le LivePilot 16 en USB à votre PC, le firmware lance un auto-test complet et affiche dans la console :
     ```text
     [DIAG] Test du bus I2C (400 kHz)...
     [DIAG] MCP #0 (0x20 - Enc 01-08) : OK !
     [DIAG] MCP #1 (0x21 - Enc 09-16) : OK !
     [DIAG] MCP #2 (0x22 - 16 Pads)    : OK !
     [DIAG] MCP #3 (0x23 - Poussoirs) : OK !
     [DIAG] Écran Gauche SPI (CS 10)  : OK !
     [DIAG] Écran Droit SPI (CS 38)   : OK !
     [DIAG] 16 LEDs NeoPixel          : OK !
     [SUCCÈS] Tous les sous-systèmes fonctionnent parfaitement.
     ```
   * Si une broche est mal enfichée, le firmware vous dit exactement :  
     `[ERREUR] MCP #1 non détecté sur le bus. Vérifiez l'alimentation 3.3V sur la puce U2.`

2. **Protections Électriques Physiques** :
   * La diode TVS empêche toute décharge électrostatique de détruire les ports USB.
   * Détrompeurs mécaniques sur les nappes de liaison.

---

## 5. Recommandation pour Vous

Si vous débutez et que vous voulez un résultat **100% professionnel, fiable et garanti sans prise de tête dès le premier allumage** :
👉 **Choisissez l'Option A (Assemblage SMT en usine)**. Vous commandez la carte sur JLCPCB avec l'assemblage coché, et vous n'aurez qu'à clipser les modules et visser la boîte comme un kit Lego d'ingénieur.
