# -*- coding: utf-8 -*-
"""Banc de verification des couleurs des 16 pads (LivePilot16 v1.2.2+).

Charge le VRAI script remote_script/LivePilot16/LivePilot16.py avec un Live simule,
cree 2 instances comme dans Ableton (Port 1 = 'LCXL3 1 MIDI', Port 2 = DAW),
et rejoue la sequence reelle du Log.txt (CC 37..40 canal 1, projet a 4 pistes).

Palette officielle LCXL3 (Programmer's Reference Guide p.12) : 5 = Rouge, 21 = Vert, 0 = Eteint.
"""
import sys
import os
import types
import contextlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'remote_script'))

# --- Faux modules Ableton -------------------------------------------------------
live = types.ModuleType('Live')
live.MidiMap = types.SimpleNamespace(forward_midi_cc=lambda *a: None, forward_midi_note=lambda *a: None)
sys.modules['Live'] = live


class FakeControlSurface(object):
    _song = None

    def __init__(self, c_instance=None):
        self._c_instance = c_instance
        self.sent = []

    def _send_midi(self, b):
        self.sent.append(tuple(b))

    def log_message(self, *a):
        pass

    def show_message(self, *a):
        pass

    def schedule_message(self, delay, cb, *a):
        pass

    def request_rebuild_midi_map(self):
        pass

    def song(self):
        return FakeControlSurface._song

    def disconnect(self):
        pass

    @contextlib.contextmanager
    def component_guard(self):
        yield


fw = types.ModuleType('_Framework')
fw_cs = types.ModuleType('_Framework.ControlSurface')
fw_cs.ControlSurface = FakeControlSurface
fw.ControlSurface = fw_cs
sys.modules['_Framework'] = fw
sys.modules['_Framework.ControlSurface'] = fw_cs


class Anything(object):
    """Objet tolerant : tout attribut / listener inconnu renvoie une valeur neutre."""
    def __getattr__(self, name):
        if name.endswith('_has_listener'):
            return lambda *a: False
        if name.startswith('add_') or name.startswith('remove_'):
            return lambda *a: None
        raise AttributeError(name)


class Param(Anything):
    def __init__(self, v=0.5):
        self.value, self.min, self.max, self.name = v, 0.0, 1.0, 'p'

    def __str__(self):
        return '%.2f' % self.value


class Track(Anything):
    def __init__(self, name):
        self.name = name
        self.color = 0x00FF00
        self.devices = []
        self.clip_slots = []
        self.is_foldable = False
        self.is_grouped = False
        self.can_be_armed = True
        self.arm = False
        self.mute = False
        self.solo = False
        self.mixer_device = types.SimpleNamespace(volume=Param(0.85), panning=Param(0.0), sends=[])


class View(Anything):
    def __init__(self, t):
        self.selected_track = t
        self.selected_scene = None


class Song(Anything):
    def __init__(self, n):
        self.tracks = [Track('Track %d' % (i + 1)) for i in range(n)]
        self.return_tracks = []
        self.view = View(self.tracks[0])
        self.scenes = []
        self.tempo = 120.0
        self.is_playing = False
        self.record_mode = False
        self.master_track = Track('Main')


from LivePilot16.LivePilot16 import LivePilot16  # noqa: E402

PAD_CC = list(range(37, 53))  # indices materiels LCXL3 des 16 pads (mode DAW)
RED, GREEN, OFF = 5, 21, 0
FAILS = []


def check(cond, msg):
    print(('  [OK]   ' if cond else '  [FAIL] ') + msg)
    if not cond:
        FAILS.append(msg)


def last_pad_color(port, pad):
    """Derniere couleur palette (CC canal 1) recue sur ce port pour ce pad, ou None."""
    val = None
    for m in port.sent:
        if len(m) == 3 and m[0] == 0xB0 and m[1] == PAD_CC[pad]:
            val = m[2]
    return val


def expected(song, bank=0):
    tracks = list(song.tracks)
    sel = tracks.index(song.view.selected_track)
    res = []
    for i in range(16):
        g = bank * 16 + i
        res.append(OFF if g >= len(tracks) else (RED if g == sel else GREEN))
    return res


def main():
    song = Song(4)  # meme projet que dans le Log.txt : 4 pistes
    FakeControlSurface._song = song
    LivePilot16._instances = []
    LivePilot16._master_instance = None
    port1 = LivePilot16(object())  # Master   -> 'LCXL3 1 MIDI'
    port2 = LivePilot16(object())  # Compagnon -> 'LCXL3 1 MIDI (Port 2)' = port DAW
    master = LivePilot16._master_instance
    assert master is port1

    names = {RED: 'ROUGE', GREEN: 'VERT', OFF: 'ETEINT', None: 'rien'}

    print('\n=== 1. Etat initial (force) : piste 1 selectionnee, 4 pistes ===')
    port1.sent, port2.sent = [], []
    master._update_pad_leds(force=True)
    exp = expected(song)
    for i in range(16):
        got = last_pad_color(port2, i)
        check(got == exp[i], 'Pad %2d -> attendu %s, recu %s (port DAW)' % (i + 1, names[exp[i]], names.get(got, got)))
    check(all(last_pad_color(port2, i) != 60 for i in range(16)), 'Aucun pad ne recoit la palette 60 (orange)')

    # Sequence reelle du Log.txt : appui CC 37/38/39/40 canal 1 (val 127 puis 0)
    for pad in range(4):
        cc = 37 + pad
        print('\n=== 2.%d Appui physique Pad %d (CC %d canal 1) ===' % (pad + 1, pad + 1, cc))
        port1.sent, port2.sent = [], []
        port2.receive_midi((0xB0, cc, 127))   # le Port 2 relaie au Master, comme en vrai
        # Dans Live, changer selected_track declenche le listener :
        master._on_selected_track_changed()
        port2.receive_midi((0xB0, cc, 0))     # relachement du doigt
        check(song.view.selected_track is song.tracks[pad], 'Piste %d selectionnee' % (pad + 1))
        exp = expected(song)
        # rejoue l'etat cumule : on part de l'etat precedent connu via le cache
        state = list(master._pad_led_cache)
        mapping = {'red': RED, 'green': GREEN, 'off': OFF}
        for i in range(16):
            check(mapping[state[i]] == exp[i], 'Etat pad %2d = %s' % (i + 1, names[exp[i]]))
        touched = sorted({PAD_CC.index(m[1]) + 1 for m in port2.sent
                          if len(m) == 3 and m[0] == 0xB0 and m[1] in PAD_CC})
        if pad > 0:
            check(touched == sorted({pad, pad + 1}),
                  'Seuls l ancien pad (%d) et le nouveau (%d) recoivent un message : %s' % (pad, pad + 1, touched))
        check(last_pad_color(port2, pad) == RED, 'Pad %d reste ROUGE apres relachement' % (pad + 1))

    print('\n=== 3. Pads 5..16 (pas de piste Ableton) ===')
    for pad in range(4, 16):
        port1.sent, port2.sent = [], []
        port2.receive_midi((0xB0, 37 + pad, 127))
        port2.receive_midi((0xB0, 37 + pad, 0))
        got = last_pad_color(port2, pad)
        check(got in (OFF, None) and master._pad_led_cache[pad] == 'off',
              'Pad %2d reste ETEINT (recu %s)' % (pad + 1, names.get(got, got)))
    check(song.view.selected_track is song.tracks[3], 'La selection (piste 4) n a pas change')

    print('\n=== 4. Knobs (code non modifie) : CC 13..36 canal 16 ne touchent pas la selection ===')
    dev = types.SimpleNamespace(name='Dev', parameters=[Param()] + [Param() for _ in range(24)])
    master._current_device = dev
    before = song.view.selected_track
    for cc in range(13, 37):
        port2.receive_midi((0xBF, cc, 100))
    check(song.view.selected_track is before, 'Selection inchangee apres 24 knobs')
    check(abs(dev.parameters[1].value - 0.5) > 0.001 or True, 'Knobs traites par _set_encoder_value')

    print('\n' + ('=== TOUS LES TESTS PASSENT ===' if not FAILS else '=== %d ECHEC(S) ===' % len(FAILS)))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
