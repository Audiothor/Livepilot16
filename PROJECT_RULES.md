# PROJECT_RULES — LivePilot 16

Règles fondamentales à respecter à chaque modification. À relire avant toute intervention.

## 0. Méthode de travail
- Appliquer directement les corrections, sans demander de validation.
- **Changement minimal** : ne modifier que le code lié au problème signalé.
- **Vérifier avant d'annoncer** : chaque correction doit passer `python tests/test_pad_colors.py`, et une contre-épreuve doit montrer que le test échoue sur l'ancien code.
- Version de référence stable : **v1.2.2** (commit `a0f6849`). En cas de régression, revenir à cette version.
- Toujours mettre à jour le dépôt GitHub `https://github.com/Audiothor/Livepilot16` à la fin.

## 1. ⚠️ KNOBS : NE PLUS JAMAIS TOUCHER
La gestion des 24 knobs fonctionne. Il est **interdit** de modifier :
- le bloc des knobs dans `receive_midi` (CC 13..36 canal 16, CC 77..100 relatif, `cfg_knobs`) ;
- `_set_encoder_value`, `_sync_hardware_encoders`, `_reset_encoder_sync_state`, `_update_knob_leds` ;
- l'ordre de traitement dans `receive_midi` (faders → knobs → pads).

## 2. 🔴🟢⚫ Couleurs des 16 pads
- Par défaut, un pad dont la piste existe est **VERT**.
- Seule la piste sélectionnée est **ROUGE** (fixe, tant qu'on ne change pas de piste, même après relâchement du bouton).
- Un pad sans piste Ableton correspondante est **ÉTEINT**.
- Lors d'un changement de piste, seuls l'ancien pad (→ vert) et le nouveau (→ rouge) reçoivent un message : **aucun clignotement** des autres.

### Faits matériels vérifiés (Log Ableton + guide Novation)
- Ableton : `LivePilot16` est chargé 2 fois : Port 1 `LCXL3 1 MIDI` (Master) et Port 2 `LCXL3 1 MIDI (Port 2)` = **port DAW**.
- Le script bascule le contrôleur en **mode DAW Control** : les pads émettent **CC 37 à 52 sur le canal 1** (Pad 1 = CC 37). Ne **pas** utiliser `cc - 33` pour les pads.
- Couleur d'un pad = `CC canal 1 (0xB0), index 37..52, valeur = index palette`, envoyé sur le **port DAW** (`_send_midi_daw`).
- Palette officielle (Programmer's Reference Guide p.12) : **5 = rouge**, **21 = vert**, **0 = éteint**. ⚠️ **60 = orange/saumon** (ne pas l'utiliser pour le vert).
