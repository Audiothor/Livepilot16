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
    ableton_remote_dir = os.path.join(user_home, "Documents", "Ableton", "User Library", "Remote Scripts")
    script_source_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "remote_script", "LivePilot16"))
    target_dir = os.path.join(ableton_remote_dir, "LivePilot16")

    print(f"[*] Source : {script_source_dir}")
    print(f"[*] Cible  : {target_dir}")

    if not os.path.exists(script_source_dir):
        print(f"[ERREUR] Le dossier source n'existe pas : {script_source_dir}")
        return False

    os.makedirs(ableton_remote_dir, exist_ok=True)

    if os.path.exists(target_dir):
        print("[!] Une installation existante a ete detectee. Remplacement...")
        if os.path.islink(target_dir):
            os.unlink(target_dir)
        else:
            shutil.rmtree(target_dir)

    try:
        # Tente de créer une jonction / lien symbolique (recommandé pour le dev en direct)
        os.symlink(script_source_dir, target_dir, target_is_directory=True)
        print("[SUCCÈS] Lien symbolique créé avec succès !")
    except Exception as e:
        print(f"[*] Info : Création de lien impossible ({e}), copie directe des fichiers...")
        shutil.copytree(script_source_dir, target_dir)
        print("[SUCCÈS] Dossier copié avec succès !")

    print("\n[OK] LivePilot 16 est maintenant disponible dans Ableton Live !")
    print("     Ouvrez Ableton Live > Préférences > Link, Tempo & MIDI > Surfaces de contrôle.")
    print("     Sélectionnez 'LivePilot 16' dans la liste déroulante.\n")
    return True

if __name__ == "__main__":
    install()
