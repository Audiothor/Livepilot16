#!/usr/bin/env python3
"""
LivePilot 16 — Script d'installation automatique du MIDI Remote Script
Crée un lien symbolique ou copie le dossier LivePilot16 dans le répertoire
officiel d'Ableton Live ("User Library/Remote Scripts").
"""

import os
import sys
import shutil

def install():
    user_home = os.path.expanduser("~")
    script_source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remote_script", "LivePilot16"))

    if not os.path.exists(script_source_dir):
        print(f"[ERREUR] Le dossier source n'existe pas : {script_source_dir}")
        return False

    target_dirs = [
        os.path.join(user_home, "Documents", "Ableton", "User Library", "Remote Scripts", "LivePilot16")
    ]

    # Détection automatique de toutes les versions d'Ableton installées (Live 11, Live 12, etc.)
    program_data_ableton = r"C:\ProgramData\Ableton"
    if os.path.exists(program_data_ableton):
        for entry in os.listdir(program_data_ableton):
            candidate = os.path.join(program_data_ableton, entry, "Resources", "MIDI Remote Scripts")
            if os.path.exists(candidate):
                target_dirs.append(os.path.join(candidate, "LivePilot16"))

    print(f"[*] Dossier source LivePilot 16 : {script_source_dir}\n")

    for target_dir in target_dirs:
        parent_dir = os.path.dirname(target_dir)
        os.makedirs(parent_dir, exist_ok=True)
        print(f"[*] Installation vers : {target_dir}")

        if os.path.exists(target_dir):
            if os.path.islink(target_dir):
                os.unlink(target_dir)
            else:
                shutil.rmtree(target_dir)

        try:
            os.symlink(script_source_dir, target_dir, target_is_directory=True)
            print("    -> [SUCCÈS] Lien symbolique créé !")
        except Exception:
            shutil.copytree(script_source_dir, target_dir)
            print("    -> [SUCCÈS] Fichiers copiés avec succès !")

    print("\n" + "=" * 65)
    print("[OK] LivePilot 16 est maintenant parfaitement installé !")
    print("=" * 65)
    print("ETAPES SUIVANTES :")
    print("1. Ouvrez Ableton Live (Live 11 ou Live 12).")
    print("2. Allez dans : Options > Préférences > Link, Tempo & MIDI.")
    print("3. Dans la section 'Surfaces de contrôle' :")
    print("   - Surface 1 : 'Launch Control XL' (Entrée / Sortie : Launch Control XL)")
    print("   - Surface 2 : 'LivePilot 16' (Entrée / Sortie : Aucun)")
    print("4. Le serveur Cockpit Web démarre automatiquement sur le port 8080.")
    print("5. Sur votre tablette (connectée au même Wi-Fi ou par câble USB) :")
    print("   Ouvrez le navigateur à l'adresse : http://192.168.1.105:8080")
    print("=" * 65 + "\n")
    return True

if __name__ == "__main__":
    install()
