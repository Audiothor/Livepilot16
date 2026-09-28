# LivePilot 16 — Guide d'Achat Complet AliExpress (Nomenclature DIY)

Ce document répertorie **chaque composant électronique exact** à commander sur AliExpress pour construire le contrôleur **LivePilot 16** (Option B - Soudure Manuelle DIY ou Prototypage).

> [!IMPORTANT]
> **Conseil pour les commandes AliExpress** :
> Chaque fiche produit propose plusieurs variantes dans un menu déroulant ("Color", "Specification" ou "Size"). **Suivez scrupuleusement la colonne "Option / Variante exacte à cocher"** pour éviter toute erreur de boîtier ou d'incompatibilité de broches.

---

## 1. Tableau Récapitulatif & Liens d'Achat Directs

| # | Composant | Rôle dans le LivePilot 16 | Qté requise (Qté à commander) | Option / Variante exacte à cocher sur AliExpress | Prix estimé | Lien direct AliExpress |
|:---:|---|---|:---:|---|:---:|:---:|
| **1** | **ESP32-S3-DevKitC-1 N16R8** | Cerveau USB/MIDI + gestion double écran DMA | 1 *(lot de 1 ou 2)* | **Variant : N16R8** (16MB Flash + 8MB PSRAM, Dual Type-C) | ~4,50 € | [Acheter ESP32-S3 N16R8](https://fr.aliexpress.com/w/wholesale-esp32-s3-n16r8.html) |
| **2** | **Microchip MCP23017-E/SP** | Expandeurs 16 I/O I2C (Encodeurs, Poussoirs, Pads) | 4 *(lot de 5 ou 10)* | **Package : DIP-28** (traversant 300mil) | ~6,00 € *(lot de 5)* | [Acheter MCP23017-E/SP DIP-28](https://fr.aliexpress.com/w/wholesale-mcp23017-dip28.html) |
| **3** | **Supports Tulipes DIP-28 Étroits** | Protection puces (soudure du support plastique vide) | 4 *(lot de 10)* | **Taille : DIP-28 Narrow / Skinny 300 mil (7.62 mm)** *(ne pas prendre 600 mil !)* | ~1,80 € *(lot de 10)* | [Acheter Supports DIP-28 300mil](https://fr.aliexpress.com/w/wholesale-dip28-socket-300mil.html) |
| **4** | **Encodeurs rotatifs EC11 avec switch** | 16 Paramètres Ableton + 1 Master Jog (Menu/BPM) | 17 *(lot de 20)* | **Axe : D-Shaft (Méplat / Demi-axe), Longueur : 20mm, 5 broches** | ~5,50 € *(lot de 20)* | [Acheter Encodeurs EC11 20mm D-shaft](https://fr.aliexpress.com/w/wholesale-ec11-rotary-encoder-20mm-d-shaft.html) |
| **5a** | **Boutons Aluminium Moletés 16mm (Paramètres)** | Knobs pour les 16 encodeurs de paramètres Ableton | 16 *(lot de 16 ou 20)* | **Diamètre : 15 à 20 mm, Axe : D-Shaft 6mm, Couleur : Noir avec repère blanc** | ~8,00 € *(lot de 20)* | [Acheter Knobs alu 6mm D-shaft](https://fr.aliexpress.com/w/wholesale-aluminum-knob-6mm-d-shaft.html) |
| **5b** | **Gros Bouton Aluminium 30mm (Master Jog)** | Gros bouton moleté DJ pour l'Encodeur #17 Master | 1 *(lot de 1)* | **Diamètre : 25 à 30 mm, Axe : 6mm, Moleté noir** | ~2,50 € | [Acheter Master Jog Knob 30mm](https://fr.aliexpress.com/w/wholesale-aluminum-knob-30mm-6mm.html) |
| **6** | **Écrans LCD TFT 3.5" IPS SPI 480x320** | Affichage dynamique (Gauche : Session/Track - Droite : Macro/FX) | 2 *(commander 2)* | **Driver : ILI9488 (ou ST7796), Type : SPI Module, Option : Without Touch (ou With Touch)** | ~18,00 € *(les 2 écrans)* | [Acheter Écran LCD 3.5" SPI ILI9488](https://fr.aliexpress.com/w/wholesale-3.5-inch-spi-tft-lcd-ili9488.html) |
| **7** | **Touches Clavier 16 Pads Translucides** | 16 touches sélection de pistes rétroéclairées RGB | 1 *(1 kit 4x4)* | **Matrice silicone translucide 4x4** (type SparkFun button pad) ou 16 boutons 12x12 avec capuchon transparent | ~5,00 € | [Acheter Matrice 4x4 silicone pad](https://fr.aliexpress.com/w/wholesale-4x4-silicone-button-pad.html) |
| **8** | **Mini PCB LEDs RGB WS2812B 5050** | Rétroéclairage individuel des 16 touches de pistes | 16 *(lot de 50 ou 100)* | **WS2812B Mini PCB 5050 (plaque ronde ou carrée 10mm individuelle)** | ~2,80 € *(lot de 50)* | [Acheter Mini PCB WS2812B 5050](https://fr.aliexpress.com/w/wholesale-ws2812b-mini-pcb.html) |
| **9** | **Switches Tactiles 12x12 + Cabochons Carrés** | 8 boutons Navigation (`◄/►`, Group, Device, Track) + 1 bouton `[VALID]` | 9 *(lot de 10 ou 20)* | **Taille : 12x12x7.3 mm + Cabochon plastique carré noir (Square Cap)** | ~2,20 € *(lot de 20)* | [Acheter Switches 12x12 capuchons](https://fr.aliexpress.com/w/wholesale-12x12x7.3-tactile-switch-square-cap.html) |
| **10** | **Kit Barrettes Sécables Femelles 2.54mm** | Connecteurs pour enficher l'ESP32 et relier les modules | 1 kit *(lot de 10 barrettes 40 broches)* | **Pitch : 2.54 mm, Type : Barrettes femelles droites (Single Row Female Header)** | ~1,50 € | [Acheter Barrettes femelles 2.54mm](https://fr.aliexpress.com/w/wholesale-2.54mm-female-pin-header.html) |
| **11** | **Kit Résistances Métalliques 1/4W Traversantes** | Résistances de Pull-up I2C (2.2kΩ), LED data (330Ω) | 1 kit assortiment | **Puissance : 1/4W (0.25W), Tolérance 1%, Traversantes (Through-hole)** | ~1,50 € *(kit complet)* | [Acheter Kit Résistances 1/4W](https://fr.aliexpress.com/w/wholesale-resistor-kit-1-4w.html) |
| **12** | **Condensateurs Céramiques 100nF (0.1µF)** | Découplage antiparasite pour l'alimentation de chaque puce | 10 *(lot de 50 ou 100)* | **Capacité : 100nF / 0.1µF (Code 104), Tension : 50V, Pitch : 2.54mm** | ~1,00 € *(lot de 50)* | [Acheter Condensateurs 100nF](https://fr.aliexpress.com/w/wholesale-ceramic-capacitor-100nf.html) |
| **13** | **Condensateurs Électrolytiques 100µF 16V/25V** | Filtrage buffer de ligne pour les 16 LEDs WS2812B | 2 *(lot de 10)* | **Capacité : 100µF (ou 470µF), Tension : 16V ou 25V, Radial traversant** | ~1,00 € *(lot de 10)* | [Acheter Condensateurs 100µF](https://fr.aliexpress.com/w/wholesale-electrolytic-capacitor-100uf-16v.html) |
| **14** | **Nappes de Câbles Dupont 2.54mm (20 cm)** | Câblage souple pour relier la façade aux cartes | 1 lot *(Femelle-Femelle + Mâle-Femelle)* | **Longueur : 20 cm, 40 pins multicolores détachables** | ~2,50 € | [Acheter Câbles Dupont 20cm](https://fr.aliexpress.com/w/wholesale-dupont-cable-ribbon-20cm.html) |

---

## 2. Coût Total Estimé de la Partie Électronique

| Catégorie | Coût Estimé |
|---|:---:|
| Cœur de calcul & I/O (ESP32-S3 N16R8 + 4x MCP23017 + Supports tulipes) | **~12,30 €** |
| Éléments de commande (17 encodeurs EC11 + 17 boutons alu + 9 boutons nav + 16 touches pads) | **~23,20 €** |
| Affichage & Visuels (2 écrans LCD 3.5" IPS ILI9488 + 50 LEDs WS2812B) | **~20,80 €** |
| Composants passifs & câblage (résistances, condensateurs, barrettes, nappes) | **~7,50 €** |
| **TOTAL ÉLECTRONIQUE COMPLET (Toutes pièces incluses)** | **~63,80 €** |

---

## 3. Détails & Pièges à Éviter sur AliExpress

### Composant #1 : ESP32-S3-DevKitC-1 N16R8
* **Attention au piège** : Il existe des dizaines de versions d'ESP32. Ne prenez **pas** d'ESP32 classique (ESP32-WROOM-32) ni d'ESP32-S2. Il vous faut obligatoirement le **ESP32-S3**.
* **Attention à la mémoire** : Choisissez impérativement l'option **N16R8** (16 Mo Flash / 8 Mo PSRAM). La mémoire PSRAM de 8 Mo est indispensable pour créer le double tampon graphique (framebuffer) des deux écrans 480x320 en 60 FPS sans ralentir la communication MIDI.
* **Ports USB** : Privilégiez les cartes à **deux ports USB-C** (un port "UART" pour la programmation / moniteur série, et un port "USB" pour le protocole MIDI USB natif d'Ableton).

### Composant #2 & #3 : MCP23017-E/SP & Supports Tulipes
* **Attention à la largeur du boîtier (300 mil vs 600 mil)** :
  * Le boîtier standard du MCP23017 traversant est un boîtier **Skinny DIP-28** (écartement entre les deux rangées de pattes de **7,62 mm / 300 mil**).
  * Lors de la commande des supports tulipes, sélectionnez impérativement **DIP-28 300 mil (Skinny / Étroit)**. Les supports 600 mil sont deux fois trop larges !

### Composant #4 : Encodeurs rotatifs EC11
* **Type d'axe** : Choisissez **D-Shaft** (axe avec un méplat plat sur un côté) ou axe cranté 6mm. Le **D-Shaft** est recommandé car les boutons en aluminium se bloquent parfaitement dessus avec une petite vis sans tête ou par emmanchement sans jamais glisser.
* **Longueur d'axe** : **20 mm** (recommandé avec le filetage et l'écrou de fixation pour serrer directement l'encodeur sur la plaque supérieure en aluminium ou le boîtier imprimé en 3D).

### Composant #6 : Écrans LCD 3.5" IPS ILI9488
* **Interface** : Vérifiez bien qu'il s'agit d'un module **SPI 8 à 14 broches** (avec broches VCC, GND, CS, RESET, DC, MOSI, SCK, LED).
* **Ne pas acheter les "Shields Arduino Uno"** : Certains écrans ILI9488 sont vendus sous forme de gros boucliers bleus avec 28 broches mâles destinés à s'emboîter sur une carte Arduino Uno (interface parallèle 8 bits). Ces écrans shields ne sont **pas** compatibles avec notre câblage SPI haute vitesse ! Prenez uniquement les modules SPI autonomes.
* **Option tactile** : Vous pouvez cocher indifféremment *Without Touch* (sans tactile) ou *With Touch* (avec tactile). Nous n'utilisons pas la fonction tactile car toutes les manipulations se font aux encodeurs et boutons physiques, mais la version avec tactile fonctionne tout aussi bien en ignorant simplement les broches tactiles `T_CS`, `T_CLK`, `T_DIN`, `T_DO`.

### Composant #8 : LEDs WS2812B sur mini PCB 5050
* Ne commandez pas des puces LED 5050 nues à souder en CMS.
* Commandez des **"WS2812B Mini PCB 5050"** (également appelées *heatsink board* ou *mini breakout*). Ce sont de minuscules pastilles rondes ou carrées de 10 mm de diamètre avec 6 pastilles de soudure bien larges au dos (`5V`, `GND`, `DIN`, `DOUT`). Elles sont ultra faciles à souder et à coller sous chaque touche silicone.

---

## 4. Matériel d'Atelier Recommandé (Si vous ne l'avez pas déjà)

Si vous n'avez pas encore d'outils de bricolage électronique, voici ce qu'il vous faut pour démarrer dans d'excellentes conditions :

1. **Kit Fer à Souder à Température Réglable (60W)** :
   * [Lien AliExpress Kit Fer à Souder](https://fr.aliexpress.com/w/wholesale-soldering-iron-kit-60w.html) (~10 € à 15 € avec support, éponge, pinces et pompe à dessouder).
2. **Fil d'Étain avec flux intégré (Sn60/Pb40 ou Sn99/Ag0.3/Cu0.7)** :
   * Diamètre recommandé : **0.8 mm** (idéal pour les broches au pas de 2.54 mm).
3. **Pince coupante de précision d'électronicien (Plato 170)** :
   * [Lien AliExpress Pince Plato 170](https://fr.aliexpress.com/w/wholesale-plato-170-cutter.html) (~1,50 € pour couper proprement les pattes des composants après soudure).
