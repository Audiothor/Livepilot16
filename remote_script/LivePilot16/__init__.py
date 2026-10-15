# LivePilot 16 — Ableton Live MIDI Remote Script
# "Ne regardez plus l'écran, pilotez votre son."

from __future__ import absolute_import, print_function, unicode_literals
from .LivePilot16 import LivePilot16

def create_instance(c_instance):
    """
    Point d'entrée officiel appelé par le moteur Ableton Live
    lorsque la surface de contrôle 'LivePilot 16' est sélectionnée.
    """
    return LivePilot16(c_instance)

def get_capabilities():
    """
    Déclare les capacités MIDI à Ableton Live pour permettre
    la sélection des ports d'entrée et de sortie (Launch Control XL / LCXL3).
    """
    try:
        from _Framework.Capabilities import (
            CONTROLLER_DESCRIPTIONS, PORTS_KEY, NOTES_CC, SCRIPT, GENERIC_SCRIPT_KEY, inport, outport
        )
        return {
            CONTROLLER_DESCRIPTIONS: [
                "Launch Control XL",
                "Launch_Control_XL_3",
                "LCXL3",
                "LivePilot 16"
            ],
            PORTS_KEY: [
                inport(props=[NOTES_CC, SCRIPT]),
                outport(props=[NOTES_CC, SCRIPT])
            ],
            GENERIC_SCRIPT_KEY: True
        }
    except Exception:
        return {}

