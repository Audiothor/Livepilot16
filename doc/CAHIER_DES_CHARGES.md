# CAHIER DES CHARGES TECHNIQUE & FONCTIONNEL
# LivePilot 16 — v1.0.0

> **Slogan :** *"Ne regardez plus l'écran d'ordinateur, pilotez votre son."*  
> **International :** *"LivePilot 16 is an interactive stage cockpit for Ableton Live, combining 16-track and 24-plugin macro control with real-time, high-visibility visual feedback on tablet."*

**Statut du projet :** Officiel — Version 1.0.0  
**Auteur / Concepteur :** Audiothor  
**Dépôt GitHub :** `https://github.com/Audiothor/Livepilot16`  
**Environnement de développement :** Antigravity IDE  

---

![LivePilot 16 Cockpit](doc/assets/tablet_cockpit_preview.jpg)

---

## 1. Vision, Identité & Concept Produit

### 1.1. Philosophie du Système
**LivePilot 16** est un cockpit scénique interactif et une surface de contrôle professionnelle conçue pour **Ableton Live 11 & 12**. Il libère le musicien et le producteur de l'écran d'ordinateur grâce à :
1. **Un affichage tête haute (HUD)** haute lisibilité sur tablette tactile (Android / iOS / PWA).
2. **Un contrôle matériel direct et sans latence** combinant un contrôleur physique de type Novation Launch Control XL (16 pistes, 24 potentiomètres) et Launchpad Pro MK3 (scènes et clips).
3. **Une synchronisation bidirectionnelle instantanée** via un Remote Script natif Python 3 et WebSocket.

$$\text{Ableton Live 12} \xleftrightarrow[\text{WebSocket + SysEx}]{\text{Temps Réel}} \text{LivePilot 16 (Python Script)} \xleftrightarrow{\text{HUD Web}} \text{Tablette Cockpit}$$

---

## 2. Spécifications de l'Interface Tablette (Stage HUD)

L'interface web est calibrée pour un usage scénique (fort contraste, éclairage sombre adapté aux clubs et festivals, typographies bold haute visibilité) :

### 2.1. Barre Supérieure (Header)
* **Bouton Menu** `≡` & **Logo officiel LIVEPILOT 16**.
* **Statut Transport & Sync** :
  * Tempo dynamique (`120 BPM`).
  * Signature rythmique (`4 / 4`).
  * Point d'accès unique : Bouton menu latéral `≡` (aucun doublon d'icône).
  * Indicateur d'état clair : `Connected` (vert néon si relié à Live) ou `Disconnected` (rouge vif si hors ligne).

### 2.2. Bandeau Scénique Hero (Progression à 3 Cartes Épurée)
* **Carte Gauche (Scène Précédente)** :
  * Bouton déclencheur `◀`.
  * Libellé `SCÈNE PRÉCÉDENTE`.
  * Numéro et titre en grand format et haute lisibilité (ex. `01 - Intro`), sans texte superflu.
* **Carte Centrale (Scène Actuelle — Hero)** :
  * Conteneur proéminent cerclé de vert néon `#00e676` avec lueur diffuse.
  * Icône Play `▶` interactive.
  * Libellé `SCÈNE ACTUELLE`.
  * Numéro et titre en très grand format (ex. `02 - Couplet`).
* **Carte Droite (Scène Suivante)** :
  * Libellé `SCÈNE SUIVANTE`.
  * Numéro et titre en grand format (ex. `03 - Refrain`).
  * Bouton déclencheur `▶`.

### 2.3. Deck Gauche — Section Pistes (Mixeur 16 Voies)
* **En-tête dynamique** : `PISTES (Banque 1/4 : Pistes 1 - 16) — Piste #02 : Bass` (rappel immédiat de la piste active).
* **Organisation en grille 8 colonnes x 2 rangées** (Pistes 1 à 8 en haut, Pistes 9 à 16 en bas).
* **Sélecteur de banques** : `◀ Banque 1 / 4 ▶` (contrôle jusqu'à 64 pistes par banques de 16).
* **Chaque tranche de console comprend** :
  * Bannière de couleur grand format (hauteur 33px) avec numéro (`11px` gras) et nom de piste (`12px` gras) ultra-lisibles sur scène.
  * **Distinction visuelle des Groupes** : Bordure en pointillés ambrée `#ffb703` et badge noir `GRP` pour identifier immédiatement les pistes de groupe.
  * Encadrement doré lumineux `#ffd600` pour la piste activement sélectionnée.
  * Double VU-mètre stéréo L/R horizontal à dégradé linéaire haute précision (Vert `#00e676` -> Jaune `#ffd600` -> Rouge `#ff3366`), avec **trait repère vertical blanc calibré à 0 dB** et graduation (`-∞`, `0 dB`, `+3`).
  * Affichage numérique du niveau crête en décibels (ex. `-4.1 dB`).
  * Ligne de panoramique avec curseur central `L • R`.

### 2.4. Deck Gauche — Paramètres du Plugin (24 Contrôles 3x8)
* **En-tête épuré et informatif** : `PLUGIN — [2/5] Serum` (index du device sur le nombre total de plugins et nom du device).
* **24 potentiomètres rotatifs compacts organisés en 3 rangées de 8**.
* Numérotation grand format explicite **`#1` à `#24`** en blanc contrasté sur fond sombre pour une visibilité immédiate en live.
* Anneau circulaire LED néon multicolore (palette arc-en-ciel contrastée).
* Curseur ponctuel lumineux indiquant la position angulaire exacte.
* Libellé du paramètre VST / Macro en clair (ex. `Cutoff`, `Drive`, `Resonance`).
* Valeur affichée en pourcentage ou unité réelle.
* Contrôle tactile bidirectionnel au glissement (drag).

### 2.5. Volet Latéral Droit (Sidebar)
* **Piste Sélectionnée** :
  * Barre d'accent doré, titre de la piste (ex. `02 - Bass`).
  * **Boutons tactiles de navigation directe** : `◀ Piste précédente` et `Piste suivante ▶` pour naviguer confortablement de piste en piste sur la tablette.
* **Device / Plugin** :
  * Carrousel de navigation avec flèches `◀` et `▶`.
  * Icône d'instrument / touches de piano.
  * Nom du plugin actif (ex. `Serum`) et éditeur (ex. `Xfer Records`).
  * Compteur de position dans la chaîne d'effets (ex. `2 / 5`).
  * Boutons de saut rapide : `◀ Device précédent` et `Device suivant ▶`.
  * Interrupteur iOS vert `Auto-follow device` (suit automatiquement le plugin sélectionné dans Live).
* **Sélecteur de Modes** :
  * `Contrôle Plugins` (mode principal actif).
  * `Mixeur`.
  * `Vue Scènes`.
* **Master Output VU-Meter Design** :
  * Double échelle stéréo L / R à dégradé continu haute luminosité.
  * Affichage crête dynamique avec libellé officiel : **`MAIN : -0.2 dB`**.
  * Graduations calibrées `-∞`, `-24`, `-12`, `-6`, `0`, `+3 dB`.

---

## 3. Architecture Logicielle & Backend Ableton

### 3.1. Structure du Répertoire
```
LivePilot16/
├── remote_script/LivePilot16/   # [ABLETON] MIDI Remote Script natif Python 3
│   ├── __init__.py              # Factory de surface de contrôle
│   ├── LivePilot16.py           # Logique LOM, listeners d'événements, WebSocket server
│   ├── consts.py                # Constantes et mappings MIDI
│   ├── web_server.py            # Serveur HTTP & WebSocket asynchrone
│   └── web/                     # Application Web Tablette (PWA)
│       ├── index.html           # Structure DOM du Cockpit
│       ├── style.css            # Feuille de style HUD sombre & réactive
│       ├── app.js               # Client WebSocket temps réel & moteur de rendu
│       ├── logo.png             # Logo officiel LIVEPILOT 16
│       └── manifest.json        # Configuration PWA plein écran
│
├── tools/                       # [OUTILS DE DÉPLOIEMENT & SIMULATION]
│   ├── install_script.py        # Script d'installation automatique dans Ableton
│   └── cockpit_bridge.py        # Simulateur et serveur de test autonome
│
└── doc/                         # [DOCUMENTATION & RENDUS]
    ├── CAHIER_DES_CHARGES.md    # Cahier des charges technique & fonctionnel
    ├── GUIDE_TABLETTE_LIVE.md   # Guide de prise en main sur scène (USB / Wi-Fi)
    └── assets/                  # Visuels et captures d'écran HD du cockpit
```

### 3.2. Protocole d'Échange Temps Réel
* **WebSocket bidirectionnel** (`/ws`) port `8080`.
* Messages JSON structurés :
  * `full_sync` : État global du Live Set (tempo, scènes, 16 pistes, 24 paramètres, périphérique actif).
  * `meters` : Télémétrie audio RMS / Peak des 16 pistes (60 fps).
  * `param_value` : Modification de valeur de potentiomètre.
  * `select_track` / `switch_bank` / `select_relative_device` / `fire_relative_scene` : Actions de navigation.

---

## 4. Guide d'Installation Rapide

1. **Déploiement du Remote Script** :
   ```bash
   python tools/install_script.py
   ```
2. **Configuration dans Ableton Live** :
   * Ouvrez `Options > Préférences > Link, Tempo & MIDI`.
   * Sélectionnez `LivePilot 16` dans les Surfaces de contrôle.
3. **Lancement sur la tablette** :
   * Connectez la tablette en Wi-Fi ou par câble USB (tethering modem USB).
   * Ouvrez le navigateur sur `http://[IP_DU_PC]:8080`.
   * Cliquez sur "Ajouter à l'écran d'accueil" pour lancer le Cockpit en plein écran.
