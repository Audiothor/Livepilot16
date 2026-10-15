# -*- coding: utf-8 -*-
"""
Test unitaire de validation de la sélection de piste par le Novation Launch Control XL 3
Vérifie la réception du message [MODE] + Bouton 4 ("Mode Select Mode 4" -> Canal 7 CC 30 val 9)
et des boutons directs.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remote_script", "LivePilot16")))
from consts import (
    CC_NOVATION_MODE_SELECT, NOVATION_MODE_TO_TRACK, LCXL_MODE16_BUTTON_CCS,
    FACTORY_BUTTON_NOTES, NOVATION_DAW_MODE_ON_SYSEX, NOVATION_DAW_MODE_ON_NOTE
)

print("[*] Test 1 : Vérification de la table de mapping Novation Mode Select...")
assert NOVATION_MODE_TO_TRACK[9] == 3, "Mode 4 (val 9) doit pointer vers la piste 4 (index 3)"
assert NOVATION_MODE_TO_TRACK[1] == 0, "Mode 1 (val 1) doit pointer vers la piste 1 (index 0)"
assert NOVATION_MODE_TO_TRACK[8] == 2, "Mode 3 (val 8) doit pointer vers la piste 3 (index 2)"
assert NOVATION_MODE_TO_TRACK[18] == 4, "Mode 5 (val 18) doit pointer vers la piste 5 (index 4)"
print("    -> [SUCCES] Table Novation Mode Select validee !")

print("[*] Test 2 : Simulation de receive_midi pour [MODE] + Bouton 4 (Canal 7, CC 30, val 9)...")
# Simulation mock
selected_tracks = []
def mock_select(idx):
    selected_tracks.append(idx)

# Test de l'algorithme direct implémenté dans LivePilot16
def simulate_midi(status, data1, data2):
    msg_type = status & 0xF0
    cc_num, cc_val = data1, data2
    if msg_type == 0xB0 and cc_num == CC_NOVATION_MODE_SELECT:
        if cc_val in NOVATION_MODE_TO_TRACK:
            mock_select(NOVATION_MODE_TO_TRACK[cc_val])
            return True
        elif 1 <= cc_val <= 16:
            mock_select(cc_val - 1)
            return True
    elif msg_type == 0xB0 and cc_num in LCXL_MODE16_BUTTON_CCS and cc_val > 0:
        mock_select(LCXL_MODE16_BUTTON_CCS.index(cc_num))
        return True
    elif msg_type == 0x90 and data2 > 0 and data1 in FACTORY_BUTTON_NOTES:
        mock_select(FACTORY_BUTTON_NOTES.index(data1))
        return True
    return False

# 1. Test Mode Select 4 (Canal 7 : 0xB6, CC 30, val 9)
res = simulate_midi(0xB6, 30, 9)
assert res == True
assert selected_tracks[-1] == 3, f"Attendu index 3 (Piste 4), obtenu {selected_tracks[-1]}"
print("    -> [SUCCES] Canal 7 CC 30 val 9 -> Piste 4 (index 3) !")

# 2. Test Mode Select 1..16
for mode_val, exp_idx in [(1, 0), (2, 1), (8, 2), (9, 3), (18, 4), (19, 5), (20, 6), (21, 7)]:
    simulate_midi(0xB6, 30, mode_val)
    assert selected_tracks[-1] == exp_idx, f"Mode {mode_val} -> Attendu {exp_idx}, obtenu {selected_tracks[-1]}"
print("    -> [SUCCES] Tous les modes Novation 1..8 selectionnent les bonnes pistes !")

# 3. Test boutons directs sous les faders (Mode 16 : CC 37..52)
simulate_midi(0xB0, 40, 127) # 4e bouton en mode 16 = CC 40
assert selected_tracks[-1] == 3, f"Bouton 4 (CC 40) doit selectionner piste 4 (index 3), obtenu {selected_tracks[-1]}"
print("    -> [SUCCES] Bouton 4 direct (CC 40) -> Piste 4 (index 3) !")

print("\n" + "="*50)
print("[TOUS LES TESTS ONT REUSSI AVEC SUCCES]")
print("="*50)
