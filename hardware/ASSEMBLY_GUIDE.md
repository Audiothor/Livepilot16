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

### Explication Détaillée des Concepts Électroniques :

#### 1. Qu'est-ce qu'un composant "Traversant" (Through-Hole / THT) ?
* **Dans les téléphones modernes (CMS / Surface Mount)** : Les composants mesurent 1 millimètre. Ils n'ont pas de pattes et sont posés à plat sur la carte. C'est quasi impossible à souder pour un débutant sans microscope.
* **Dans le LivePilot 16 (Traversant / THT)** : C'est la méthode traditionnelle et robuste des amplificateurs et pédales de guitare. Chaque composant possède de **vraies pattes métalliques solides** d'environ 1 cm de long :
  ```text
  Composant (au-dessus)
      │     │  (Pattes métalliques solides)
  ════╪═════╪════  ◄── Circuit Imprimé (PCB) avec de gros trous
      │     │
     (▲)   (▲) ◄── Une simple goutte d'étain déposée au dos avec le fer !
  ```
  * L'écartement entre les pattes est de **2,54 mm** (le standard international "Breadboard"), ce qui laisse un espace énorme pour poser le fer sans trembler ni toucher la patte voisine.

---

#### 2. Qu'est-ce qu'un "Support Tulipe" (DIP Socket) et pourquoi cela protège vos puces ?
Une puce électronique (comme le processeur ou l'expandeur MCP23017) craint les coups de chaud prolongés. Si un débutant laisse son fer à souder 15 secondes sur une patte par hésitation, il pourrait surchauffer la puce.
Pour éliminer ce risque à 100%, on utilise un **support de circuit intégré** (appelé *support tulipe* ou *DIP socket*) :

```text
ÉTAPE 1 : On soude le SUPPORT EN PLASTIQUE VIDE sur le circuit
          (Aucun composant électronique dedans, 0% risque de surchauffe !)
          ┌───────────────────────────┐
          │  Support Tulipe (Plastique)│
          └──┬──┬──┬──┬──┬──┬──┬──┬──┬┘
             │  │  │  │  │  │  │  │  │ ◄── Broches à souder tranquillement
             
ÉTAPE 2 : Une fois la plaque froide, on CLIPSE la puce dedans avec les doigts !
          ┌───────────────────────────┐
          │  Puce MCP23017 (Délicate) │
          └──┬──┬──┬──┬──┬──┬──┬──┬──┬┘
             ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  ▼  (Enfichage doux sans fer à souder !)
          ┌───────────────────────────┐
          │     Support Tulipe        │
          └───────────────────────────┘
```
* **Résultat** : La puce ne touche **JAMAIS** le fer à souder !
* **Bonus maintenance** : Si un jour une puce est défectueuse, vous la déclipsez avec un petit tournevis plat et vous en remettez une neuve en 5 secondes, sans jamais dessouder !

---

### Liens Commerciaux des Pièces pour l'Option B :

1. **La Plaque Électronique Dédiée (PCB)** :
   * Une plaque sur-mesure coûte **environ 2 $ à 5 $ pour 5 exemplaires** sur [JLCPCB.com](https://jlcpcb.com) ou [PCBWay.com](https://www.pcbway.com). On y dépose simplement le dossier zippé `hardware/gerber/` généré par le projet. La plaque arrive pré-percée, avec les pistes de cuivre prêtes et le nom de chaque composant imprimé en blanc.
2. **Les Supports Tulipes DIP-28 (Lot pour les 4 MCP23017)** :
   * [Amazon France — Lot de supports CI DIP-28](https://www.amazon.fr/s?k=support+dip+28+broches) (~5 € le lot de 10)
   * [Gotronic France — Support lyre / tulipe DIP28](https://www.gotronic.fr/art-support-tulipe-28-broches-sup28t-4261.htm) (~0,60 € pièce)
3. **Les Puces I2C en boîtier traversant (DIP-28)** :
   * Référence exacte : **MCP23017-E/SP** (le suffixe `-SP` signifie boîtier DIP à longues pattes traversantes)
   * [Gotronic France — Circuit MCP23017-E/SP](https://www.gotronic.fr/art-circuit-mcp23017-sp-17482.htm) (~1,90 € pièce)
   * [Mouser France — MCP23017-E/SP DIP-28](https://www.mouser.fr/ProductDetail/Microchip-Technology/MCP23017-E-SP)
4. **Le Fer à Souder Débutant & Étain** :
   * Un kit fer à souder à température réglable (avec pompe à dessouder et fil d'étain) :
   * [Amazon France — Kit Fer à Souder 60W avec accessoires](https://www.amazon.fr/s?k=kit+fer+a+souder+electronique) (~18 € à 22 € le kit complet).

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
