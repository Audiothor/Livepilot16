# GUIDE OFFICIEL : CONFIGURATION DU LIVE SANS ÉCRAN
## Ableton Live + Tablette Android (Cockpit HUD) + Launch Control XL + Launchpad Pro MK3

> **Slogan :** *"Ne regardez plus l'écran d'ordinateur, pilotez votre son."*

---

## 1. Pourquoi ce pivot est la meilleure décision pour votre Live

Vous avez pris une excellente décision d'abandonner la fabrication artisanale lourde en soudures.
En combinant du matériel industriel réputé avec votre tablette Android, vous obtenez :
- **Zéro soudure, zéro risque de faux contact sur scène.**
- **Qualité de fabrication irréprochable** (pads et faders Novation calibrés pour tourner en tournée).
- **Affichage haute résolution couleur géant** sur votre tablette Android (bien plus grand, net et lisible que deux petits écrans TFT 3.5").
- **Votre ordinateur portable peut rester fermé sous la table ou dans un rack.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    TABLETTE ANDROID : COCKPIT HUD STAGE                     │
│  [TEMPO / BAR] [BANDEAU SCÈNE EN COURS (COULEUR)] [8 TRANCHES VU-MÈTRES]    │
│            [CHAÎNE DE PLUGINS] [24 POTARDS VALEURS EN CLAIR]                │
└─────────────────────────────────────────────────────────────────────────────┘
                               ▲ (Câble USB ou Wi-Fi)
┌───────────────────────────────┴─────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────────────────┐       ┌─────────────────────────────┐      │
│  │      LAUNCHPAD PRO MK3      │       │      LAUNCH CONTROL XL      │      │
│  │  • Lancement des scènes     │       │  • 8 Faders de volume       │      │
│  │  • Déclenchement des clips  │       │  • 24 Knobs (3 rangées x 8) │      │
│  │  • Stop / Mute / Solo / Arm │       │  • Contrôle plugins & EQ    │      │
│  │  • Jeu d'instruments (Pads) │       │  • Track / Device Navigation│      │
│  └─────────────────────────────┘       └─────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                               ▲ (USB)
┌─────────────────────────────────────────────────────────────────────────────┐
│       ORDINATEUR PORTABLE (ABLETON LIVE 12) — ÉCRAN FERMÉ SOUS LA TABLE     │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Rôle précis de chaque élément sur scène

| Matériel | Rôle Principal | Ce que vous faites avec vos mains / yeux |
|---|---|---|
| **Launchpad Pro MK3** | **Matrice de jeu & Scènes** | • Lancer les scènes du morceau (colonne droite).<br>• Déclencher les clips audio / MIDI.<br>• Jouer des synthétiseurs en mode Note.<br>• Activer les mutes / solos rapides. |
| **Launch Control XL** | **Mixage & Contrôle des Plugins** | • Mixer les 8 pistes avec les 8 faders physiques.<br>• Tweaker les 24 potentiomètres (filtres, réverbes, synthés, macros).<br>• Naviguer de device en device sur la piste sélectionnée. |
| **Tablette Android** | **Cockpit Visuel (Affichage Tête Haute)** | • **Lire en gros la scène en cours** (avec la couleur exacte Ableton).<br>• **Voir les VU-mètres réels (L/R)** et le nom des 8 pistes.<br>• **Voir en clair ce que font les 24 boutons** du Launch Control XL (ex: *"Cutoff 2.4 kHz"*, *"Reso 45%"*, *"Drive +6dB"*).<br>• Suivre le tempo BPM et la mesure en cours (`BAR 17.2`). |
| **PC Portable** | **Moteur Audio Invisible** | Posé sous la table, écran rabattu, génère le son et héberge Ableton Live. |

---

## 3. Installation et Configuration en 3 Étapes

### Étape 1 : Le Remote Script Ableton (Déjà installé !)
Le script **LivePilot 16** a été déployé directement dans votre dossier utilisateur Ableton :
`C:\Users\comme\Documents\Ableton\User Library\Remote Scripts\LivePilot16`

1. Ouvrez **Ableton Live 12**.
2. Allez dans **Options > Préférences > Link, Tempo & MIDI**.
3. Dans la liste des **Surfaces de contrôle**, configurez :
   - Ligne 1 : **Launchpad Pro MK3** (Entrée & Sortie : vos ports Launchpad Pro MK3).
   - Ligne 2 : **Launch Control XL** (Entrée & Sortie : vos ports Launch Control XL).
   - Ligne 3 : **LivePilot 16** (Entrée / Sortie : `Aucun` ou votre port MIDI virtuel si vous en avez un, ce n'est pas obligatoire car le script communique directement en réseau avec la tablette !).

Dès qu'Ableton démarre avec *LivePilot 16*, le serveur Cockpit est automatiquement actif sur le port `8080`.

---

### Étape 2 : Connecter la Tablette Android

Vous avez deux façons de connecter votre tablette au PC :

#### Option A (RECOMMANDÉE POUR LE LIVE) : Connexion par Câble USB (Tethering)
> [!TIP]
> **Pourquoi le câble USB est le meilleur choix sur scène :**
> - **Zéro latence** (liaison réseau câblée directe).
> - **Recharge continue** : la tablette reste branchée au PC et ne tombera jamais en panne de batterie en plein milieu d'un set.
> - **Zéro interférence** : aucun risque de déconnexion Wi-Fi due aux téléphones du public ou aux ondes de la salle.

1. Branchez votre tablette Android à l'ordinateur portable avec son câble USB.
2. Sur la tablette Android, allez dans :  
   **Paramètres > Connexions > Point d'accès mobile et modem > Modem USB** (ou *Partage de connexion USB*). Activez-le.
3. Windows reconnaît instantanément la tablette comme une carte réseau locale (adresse type `192.168.42.x`).
4. Ouvrez **Chrome** sur votre tablette et tapez l'adresse de votre PC (ex: `http://192.168.42.129:8080` ou votre adresse IP locale).

#### Option B : Connexion sans fil (Wi-Fi ou Hotspot PC)
1. Connectez la tablette et le PC sur le même réseau Wi-Fi (ou créez un point d'accès mobile depuis Windows).
2. Ouvrez **Chrome** sur la tablette et accédez à :  
   `http://192.168.1.105:8080` *(remplacez par l'IP de votre PC affichée dans Ableton)*.

---

### Étape 3 : Transformer la page en Application Plein Écran Pro (PWA)

Pour que l'affichage prenne **100% de la surface de la tablette** sans aucune barre d'adresse ni boutons parasites :
1. Dans Chrome sur votre tablette Android, appuyez sur les **3 petits points verticaux** (menu en haut à droite).
2. Sélectionnez **"Ajouter à l'écran d'accueil"** (ou *"Installer l'application"*).
3. Une icône **"LivePilot Cockpit"** apparaît sur l'écran d'accueil de la tablette.
4. Lancez-la : la voilà en mode plein écran immersif (Kiosk Mode).
5. **Anti-veille automatique intégrée** : Le Cockpit active automatiquement la *Wake Lock API*, votre tablette ne s'éteindra jamais toute seule pendant que vous jouez.

---

## 4. Test et Simulation Hors-Ligne (Même sans Ableton)

Si vous voulez tester le rendu visuel sur votre tablette immédiatement, sans même lancer Ableton :
1. Dans votre terminal Antigravity / PowerShell, lancez :
   ```powershell
   python tools/cockpit_bridge.py
   ```
2. Ouvrez l'adresse indiquée sur votre tablette : vous verrez les 8 tranches de mix, les VU-mètres s'animer à 25 FPS, les 24 boutons tourner, et le bandeau de scène s'afficher en grand !

---

## 5. Comment se déroule votre Live sur scène

1. **Vous lancez votre morceau :**
   - Appuyez sur la touche Scene Launch de votre **Launchpad Pro MK3**.
   - Immédiatement, le bandeau de la tablette s'illumine avec le nom de la scène en très grand (ex: `03 - MAIN DROP`) et sa couleur exacte Ableton Live.
   - Les VU-mètres s'animent sur la tablette en temps réel.
2. **Vous voulez retravailler le synthé de la piste 5 :**
   - Appuyez sur le bouton de sélection de la piste 5 sur le **Launch Control XL** (ou touchez la piste sur la tablette).
   - La tablette affiche instantanément la chaîne d'effets du synthé et assigne les 24 potentiomètres.
   - Tournez le premier potentiomètre du Launch Control XL : le cadran virtuel tourne sur la tablette et affiche la valeur exacte : `Cutoff : 2.40 kHz`.
3. **Pendant tout le concert :**
   - Vos mains sont sur les faders et les pads.
   - Vos yeux sont sur la tablette juste au-dessus.
   - **L'ordinateur portable reste fermé, silencieux et oublié.**
