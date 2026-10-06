# GUIDE OFFICIEL : CONFIGURATION DU LIVE SANS ÉCRAN
## Ableton Live 11/12 + Tablette (Cockpit HUD) + Launch Control XL + Launchpad Pro MK3

> **Slogan :** *"Ne regardez plus l'écran d'ordinateur, pilotez votre son."*  
> **International :** *"LivePilot 16 is an interactive stage cockpit for Ableton Live, combining 16-track and 24-plugin macro control with real-time, high-visibility visual feedback on tablet."*

---

![LivePilot 16 Stage HUD](assets/tablet_cockpit_preview.jpg)

---

## 1. Pourquoi cette configuration est optimale pour la scène

1. **Zéro manipulation d'écran d'ordinateur** : Votre PC portable reste sous la table ou dans un rack de tournée avec l'écran rabattu.
2. **Contrôle physique franc et ergonomique** : Faders de volume et 24 potentiomètres physiques sous les doigts avec le Launch Control XL, matrice de clips/scènes sur le Launchpad Pro MK3.
3. **Affichage tête haute géant sur tablette** : 
   - Déroulé chronologique clair des scènes (**Scène précédente**, **Scène en cours en vert néon**, **Scène suivante**).
   - Vue d'ensemble immédiate sur **16 pistes simultanées (2 rangées de 8)** avec VU-mètres stéréo et panoramiques.
   - Traduction instantanée des **24 potentiomètres** en valeurs et libellés réels (ex. `Cutoff 72 %`, `Sub Level 81 %`, `FM Amount 46 %`).
   - Carrousel des périphériques avec mode **Auto-follow device**.

---

## 2. Rôle précis de chaque équipement en concert

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TABLETTE : COCKPIT HUD STAGE                          │
│   [BPM/SYNC] [BANDEAU 3 SCÈNES : PRÉCÉDENTE / EN COURS / SUIVANTE]          │
│   [MIXEUR 16 PISTES (2x8)] [24 MACROS PLUGINS (3x8)] [SIDEBAR DEVICE/MODES] │
└─────────────────────────────────────────────────────────────────────────────┘
                                ▲ (USB Câble ou Wi-Fi)
┌───────────────────────────────┴─────────────────────────────────────────────┐
│                                                                             │
│  ┌─────────────────────────────┐       ┌─────────────────────────────┐      │
│  │      LAUNCHPAD PRO MK3      │       │      LAUNCH CONTROL XL      │      │
│  │  • Lancement des scènes     │       │  • 16 Boutons de pistes     │      │
│  │  • Déclenchement des clips  │       │  • 24 Potentiomètres (3x8)  │      │
│  │  • Stop / Mute / Solo / Arm │       │  • 8 Faders physiques       │      │
│  │  • Jeu d'instruments (Pads) │       │  • Navigation Track/Device  │      │
│  └─────────────────────────────┘       └─────────────────────────────┘      │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                ▲ (USB)
┌─────────────────────────────────────────────────────────────────────────────┐
│      ORDINATEUR PORTABLE (ABLETON LIVE 11/12) — ÉCRAN FERMÉ SOUS LA TABLE   │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Matériel | Rôle Principal | Utilisation Scène |
|---|---|---|
| **Tablette tactile** | **Cockpit Visuel HUD** | Vue temps réel de la progression du set, des niveaux audio des 16 pistes, des paramètres des VST et de la chaîne de plugs. |
| **Launch Control XL** | **Mixage & Filtres** | Manipulation physique des faders de volume, contrôle immédiat des 24 potentiomètres et sélection des 16 canaux. |
| **Launchpad Pro MK3** | **Séquenceur & Jeu** | Déclenchement des clips, transitions de scènes et jeu d'instruments MIDI. |
| **PC Portable** | **Moteur Audio** | Hébergement silencieux d'Ableton Live. |

---

## 3. Mise en Route Rapide

### Étape 1 : Installation du Remote Script
Exécutez dans un terminal :
```bash
python tools/install_script.py
```
Dans **Ableton Live** :
- `Options > Préférences > Link, Tempo & MIDI`.
- Surface de contrôle 1 : `Launch Control XL`.
- Surface de contrôle 2 : `Launchpad Pro MK3`.
- Surface de contrôle 3 : `LivePilot 16` (Entrée / Sortie : `Aucun`).

### Étape 2 : Connexion Tablette
- **Option Scène (Câble USB - Recommandée)** : Branchez la tablette en USB au PC, activez le *Modem USB* (partage de connexion).
- **Option Répétition (Wi-Fi)** : Connectez la tablette au réseau local du PC.
- Ouvrez le navigateur sur `http://[IP_DU_PC]:8080`.
- Ajoutez la page à l'écran d'accueil pour profiter de l'expérience plein écran PWA native.
