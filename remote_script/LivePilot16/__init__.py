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
