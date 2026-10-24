# -*- coding: utf-8 -*-
# LivePilot 16 — Module Principal du Remote Script Ableton Live
# Architecture Live Cockpit : Launch Control XL + Launchpad Pro MK3 + Tablette Android (HUD)
# "Ne regardez plus l'écran, pilotez votre son."

from __future__ import absolute_import, print_function, unicode_literals
import os
import json
import copy
import Live
from _Framework.ControlSurface import ControlSurface
from .consts import (
    SYSEX_HEADER, CMD_BANK_INFO, CMD_TRACK_ACTIVE, CMD_BANK_COLORS,
    CMD_DEVICE_ACTIVE, CMD_PARAM_DATA, CMD_SCENE_INFO, CC_BASE_ENCODERS,
    DEFAULT_KNOB_CCS, DEFAULT_FADER_CCS, DEFAULT_BUTTON_CCS, DEFAULT_MIDI_CHANNEL,
    FACTORY_KNOB_CCS, FACTORY_BUTTON_NOTES, LCXL_MODE16_BUTTON_CCS,
    CC_NOVATION_MODE_SELECT, NOVATION_MODE_TO_TRACK,
    NOVATION_DAW_MODE_ON_SYSEX, NOVATION_DAW_MODE_OFF_SYSEX,
    NOVATION_DAW_MODE_ON_NOTE, NOVATION_DAW_MODE_OFF_NOTE,
    CC_ENC17_JOG, CC_ENC17_PUSH, CC_NAV_LEFT, CC_NAV_RIGHT, CC_BTN_VALID,
    CC_NAV_TRACK_PREV, CC_NAV_TRACK_NEXT, CC_NAV_GROUP_PREV, CC_NAV_GROUP_NEXT,
    CC_NAV_DEV_PREV, CC_NAV_DEV_NEXT, CC_BASE_TRACK_SEL,
    NUM_TRACKS_PER_BANK, NUM_ENCODERS, DEFAULT_HTTP_PORT,
    NOVATION_FEATURE_CONTROLS_ON_NOTE, LCXL3_BUTTON_INDICES, LCXL3_RGB_SYSEX_HEADER,
    CC_NAV_TRACK_LEFT, CC_NAV_TRACK_RIGHT, CC_NAV_PAGE_UP, CC_NAV_PAGE_DOWN,
    DAW_FADER_CCS, DAW_KNOB_CCS, DAW_BUTTON_CCS,
    CC_HW_PLAY, CC_HW_RECORD, CC_HW_SOLO_ARM, CC_HW_MUTE_SELECT, CC_HW_CLIP_STOP,
    NOVATION_SURFACE_DAW_MIXER, NOVATION_SURFACE_DAW_CONTROL,
    NOVATION_ENCODER_ROW1_ABS, NOVATION_ENCODER_ROW2_ABS, NOVATION_ENCODER_ROW3_ABS,
    DEFAULT_NAV_BUTTONS, LIVEPILOT_VERSION
)
from .web_server import LivePilotWebServer

def int_to_hex_color(color_int):
    """Convertit une couleur entière Ableton en code hexadécimal CSS #RRGGBB"""
    if color_int is None:
        return "#444b60"
    r = (color_int >> 16) & 0xFF
    g = (color_int >> 8) & 0xFF
    b = color_int & 0xFF
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

class LivePilot16(ControlSurface):
    _master_instance = None
    _instances = []

    def __init__(self, c_instance):
        super(LivePilot16, self).__init__(c_instance)
        LivePilot16._instances.append(self)
        self._is_master = False
        if LivePilot16._master_instance is None:
            LivePilot16._master_instance = self
            self._is_master = True

        self.log_message("LivePilot : Initialisation Remote Script (%s)..." % ("MASTER (Port 1)" if self._is_master else "COMPAGNON (Port 2)"))

        self._current_bank_index = 0
        self._current_track = None
        self._observed_track = None
        self._assigned_devices = []
        self._current_device_idx = 0
        self._current_device = None
        self._observed_params = []
        self._observed_scenes = []
        self._observed_clip_tracks = []
        self._master_mode_bpm = True
        self._meter_polling_active = False
        self._lcxl3_surface_mode = 'daw'
        self._updating_from_hardware = False
        self._encoder_synced = [False] * NUM_ENCODERS
        self._encoder_last_raw = [None] * NUM_ENCODERS
        self._pad_led_cache = [None] * NUM_TRACKS_PER_BANK
        self._knob_led_cache = [None] * NUM_ENCODERS

        # Configuration MIDI du Launch Control XL (par défaut : LivePilot CC 1..24 & CC 25..40)
        self._midi_config = {
            'preset': 'livepilot',
            'channel': DEFAULT_MIDI_CHANNEL,
            'knobs': list(DEFAULT_KNOB_CCS),
            'buttons': list(DEFAULT_BUTTON_CCS),
            'button_type': 'cc',
            'nav_buttons': copy.deepcopy(DEFAULT_NAV_BUTTONS)
        }
        self._load_midi_config_from_disk()

        # Démarrage du serveur Web / WebSocket UNIQUEMENT sur l'instance Master
        if self._is_master:
            self._web_server = LivePilotWebServer(
                port=DEFAULT_HTTP_PORT,
                on_client_message=self._on_web_client_message,
                logger=self.log_message
            )
            self._web_server.start()
        else:
            self._web_server = None

        # Initialisation du moteur LOM
        if self._is_master:
            with self.component_guard():
                self._setup_listeners()
                self._full_resync()
                try:
                    self.request_rebuild_midi_map()
                except Exception:
                    pass
            self._schedule_meter_poll()
        else:
            with self.component_guard():
                try:
                    self.request_rebuild_midi_map()
                except Exception:
                    pass
            # Pour l'instance compagnon (Port 2) : lancer une resynchronisation complète depuis le Master
            if LivePilot16._master_instance:
                try:
                    self.schedule_message(1, LivePilot16._master_instance._full_resync)
                except Exception:
                    pass

        self.log_message("LivePilot : Pret pour le Live !")

    def disconnect(self):
        """Nettoyage lors de la fermeture d'Ableton Live"""
        self.log_message("LivePilot : Deconnexion de la surface de controle.")
        if self in LivePilot16._instances:
            LivePilot16._instances.remove(self)
        if LivePilot16._master_instance is self:
            LivePilot16._master_instance = LivePilot16._instances[0] if LivePilot16._instances else None
        try:
            self._send_midi(NOVATION_DAW_MODE_OFF_SYSEX)
            self._send_midi(NOVATION_DAW_MODE_OFF_NOTE)
        except Exception:
            pass
        if self._web_server:
            self._web_server.stop()
            self._web_server = None
        if self._is_master:
            self._cleanup_listeners()
            self._detach_scene_listeners()
            self._detach_track_devices_listener()
            self._detach_track_clip_listeners()
            self._remove_parameter_listeners()
        super(LivePilot16, self).disconnect()

    def update(self):
        super(LivePilot16, self).update()
        if self._is_master:
            self._update_pad_leds(force=True)
            self._update_knob_leds(force=True)
            self._update_nav_leds()
            self._sync_hardware_encoders()

    # =========================================================================
    # ÉCOUTEURS DU LIVE OBJECT MODEL (LOM)
    # =========================================================================
    def _setup_listeners(self):
        song = self.song()
        if not song.view.selected_track_has_listener(self._on_selected_track_changed):
            song.view.add_selected_track_listener(self._on_selected_track_changed)
        if not song.tracks_has_listener(self._on_tracks_changed):
            song.add_tracks_listener(self._on_tracks_changed)
        if not song.tempo_has_listener(self._on_tempo_changed):
            song.add_tempo_listener(self._on_tempo_changed)
        if not song.is_playing_has_listener(self._on_play_state_changed):
            song.add_is_playing_listener(self._on_play_state_changed)
        if not song.scenes_has_listener(self._on_scenes_list_changed):
            song.add_scenes_listener(self._on_scenes_list_changed)
        if not song.view.selected_scene_has_listener(self._on_scene_selection_changed):
            song.view.add_selected_scene_listener(self._on_scene_selection_changed)
        if hasattr(song, 'master_track') and song.master_track and hasattr(song.master_track, 'mixer_device'):
            vol = song.master_track.mixer_device.volume
            if not vol.value_has_listener(self._on_master_volume_changed):
                vol.add_value_listener(self._on_master_volume_changed)
        self._attach_scene_listeners()
        self._attach_track_clip_listeners()

    def _cleanup_listeners(self):
        song = self.song()
        if hasattr(song, 'master_track') and song.master_track and hasattr(song.master_track, 'mixer_device'):
            vol = song.master_track.mixer_device.volume
            if vol.value_has_listener(self._on_master_volume_changed):
                vol.remove_value_listener(self._on_master_volume_changed)
        if song.view.selected_track_has_listener(self._on_selected_track_changed):
            song.view.remove_selected_track_listener(self._on_selected_track_changed)
        if song.tracks_has_listener(self._on_tracks_changed):
            song.remove_tracks_listener(self._on_tracks_changed)
        if song.tempo_has_listener(self._on_tempo_changed):
            song.remove_tempo_listener(self._on_tempo_changed)
        if song.is_playing_has_listener(self._on_play_state_changed):
            song.remove_is_playing_listener(self._on_play_state_changed)
        if song.scenes_has_listener(self._on_scenes_list_changed):
            song.remove_scenes_listener(self._on_scenes_list_changed)
        if song.view.selected_scene_has_listener(self._on_scene_selection_changed):
            song.view.remove_selected_scene_listener(self._on_scene_selection_changed)
        self._detach_track_devices_listener()
        self._detach_track_clip_listeners()

    def _attach_scene_listeners(self):
        self._detach_scene_listeners()
        for sc in self.song().scenes:
            try:
                if not sc.is_playing_has_listener(self._on_scene_status_changed):
                    sc.add_is_playing_listener(self._on_scene_status_changed)
                if not sc.name_has_listener(self._on_scene_status_changed):
                    sc.add_name_listener(self._on_scene_status_changed)
                if not sc.color_has_listener(self._on_scene_status_changed):
                    sc.add_color_listener(self._on_scene_status_changed)
                self._observed_scenes.append(sc)
            except Exception:
                pass

    def _detach_scene_listeners(self):
        for sc in self._observed_scenes:
            try:
                if sc.is_playing_has_listener(self._on_scene_status_changed):
                    sc.remove_is_playing_listener(self._on_scene_status_changed)
                if sc.name_has_listener(self._on_scene_status_changed):
                    sc.remove_name_listener(self._on_scene_status_changed)
                if sc.color_has_listener(self._on_scene_status_changed):
                    sc.remove_color_listener(self._on_scene_status_changed)
            except Exception:
                pass
        self._observed_scenes = []

    def _on_tempo_changed(self):
        self._send_scene_info()
        self._broadcast_transport()

    def _on_master_volume_changed(self):
        if not self._web_server:
            return
        m_vol = self.song().master_track.mixer_device.volume
        self._web_server.broadcast({
            'type': 'master_volume',
            'data': {
                'value': round(float(m_vol.value), 3),
                'str': str(m_vol)
            }
        })

    def _on_play_state_changed(self):
        self._send_scene_info()
        self._broadcast_transport()

    def _on_scenes_list_changed(self):
        self._attach_scene_listeners()
        self._send_scene_info()
        self._broadcast_active_scene()
        self._broadcast_selected_track()

    def _on_scene_selection_changed(self):
        self._send_scene_info()
        self._broadcast_active_scene()
        self._broadcast_selected_track()

    def _on_scene_status_changed(self):
        self._send_scene_info()
        self._broadcast_active_scene()
        self._broadcast_selected_track()

    def _on_tracks_changed(self):
        self._attach_track_clip_listeners()
        self._update_pad_leds(force=True)
        self._update_knob_leds(force=True)
        self._update_nav_leds()
        self._send_bank_info()
        self._send_bank_colors()
        self._broadcast_full_sync()

    def _attach_track_clip_listeners(self):
        self._detach_track_clip_listeners()
        for t in self.song().tracks:
            try:
                if hasattr(t, 'playing_slot_index_has_listener') and not t.playing_slot_index_has_listener(self._on_track_clip_state_changed):
                    t.add_playing_slot_index_listener(self._on_track_clip_state_changed)
                    self._observed_clip_tracks.append(t)
                if hasattr(t, 'fired_slot_index_has_listener') and not t.fired_slot_index_has_listener(self._on_track_clip_state_changed):
                    t.add_fired_slot_index_listener(self._on_track_clip_state_changed)
            except Exception:
                pass

    def _detach_track_clip_listeners(self):
        for t in getattr(self, '_observed_clip_tracks', []):
            try:
                if hasattr(t, 'playing_slot_index_has_listener') and t.playing_slot_index_has_listener(self._on_track_clip_state_changed):
                    t.remove_playing_slot_index_listener(self._on_track_clip_state_changed)
                if hasattr(t, 'fired_slot_index_has_listener') and t.fired_slot_index_has_listener(self._on_track_clip_state_changed):
                    t.remove_fired_slot_index_listener(self._on_track_clip_state_changed)
            except Exception:
                pass
        self._observed_clip_tracks = []

    def _on_track_clip_state_changed(self):
        self._broadcast_selected_track()

    def _get_active_scene_index(self):
        song = self.song()
        for idx, sc in enumerate(song.scenes):
            if getattr(sc, 'is_playing', False):
                return idx
        try:
            return list(song.scenes).index(song.view.selected_scene)
        except Exception:
            return 0

    def _on_selected_track_changed(self):
        # Auto-follow désactivé depuis la tablette : la piste/device contrôlé reste verrouillé
        if not getattr(self, '_auto_follow', True):
            return
        self._current_track = self.song().view.selected_track
        # Aligne automatiquement la banque si la piste sélectionnée est hors de la banque courante
        self._auto_align_bank_for_track(self._current_track)
        self._attach_track_devices_listener()
        self._refresh_assigned_devices()
        self._reset_encoder_sync_state()
        # Mise à jour matérielle immédiate et prioritaire (sans jamais faire clignoter les autres pads)
        self._update_pad_leds()
        self._update_knob_leds()
        self._update_nav_leds()
        self._sync_hardware_encoders()
        self._update_screen_display()
        self._send_active_track_info()
        self._send_bank_colors()
        self._send_active_device_info()
        self._send_parameters_info()
        self._broadcast_selected_track()

    def _auto_align_bank_for_track(self, track):
        """Ajuste automatiquement la banque visible de 16 pistes si nécessaire"""
        tracks = list(self.song().tracks)
        if track in tracks:
            idx = tracks.index(track)
            target_bank = idx // NUM_TRACKS_PER_BANK
            if target_bank != self._current_bank_index:
                self._current_bank_index = target_bank
                self._pad_led_cache = [None] * NUM_TRACKS_PER_BANK
                self._send_bank_info()
                self._send_bank_colors()

    def _attach_track_devices_listener(self):
        self._detach_track_devices_listener()
        if self._current_track and hasattr(self._current_track, 'devices_has_listener'):
            try:
                if not self._current_track.devices_has_listener(self._on_track_devices_changed):
                    self._current_track.add_devices_listener(self._on_track_devices_changed)
                    self._observed_track = self._current_track
            except Exception:
                pass

    def _detach_track_devices_listener(self):
        if getattr(self, '_observed_track', None):
            try:
                if hasattr(self._observed_track, 'devices_has_listener') and self._observed_track.devices_has_listener(self._on_track_devices_changed):
                    self._observed_track.remove_devices_listener(self._on_track_devices_changed)
            except Exception:
                pass
            self._observed_track = None

    def _on_track_devices_changed(self):
        self._refresh_assigned_devices()
        self._reset_encoder_sync_state()
        self._sync_hardware_encoders()
        self._send_active_device_info()
        self._send_parameters_info()
        self._broadcast_selected_track()
        self._update_knob_leds()
        self._update_nav_leds()

    # =========================================================================
    # GESTION DES DEVICES & PARAMÈTRES
    # =========================================================================
    def _device_has_assignments(self, device):
        if not device:
            return False
        return len(device.parameters) >= 1

    def _track_has_assignments(self, track):
        if not track:
            return False
        for dev in track.devices:
            if self._device_has_assignments(dev):
                return True
        return False

    def _refresh_assigned_devices(self):
        self._remove_parameter_listeners()
        self._assigned_devices = []
        if self._current_track:
            for dev in self._current_track.devices:
                if self._device_has_assignments(dev):
                    self._assigned_devices.append(dev)

        if len(self._assigned_devices) > 0:
            self._current_device_idx = 0
            self._current_device = self._assigned_devices[0]
            self._attach_parameter_listeners()
        else:
            self._current_device_idx = 0
            self._current_device = None

    def _can_navigate_devices(self):
        return len(self._assigned_devices) > 1

    def _nav_device_prev(self):
        """Sélectionne le plugin -1 de la piste actuelle (s'il existe, sans boucler)"""
        if not self._assigned_devices or self._current_device_idx <= 0:
            self._update_nav_leds()
            return
        self._current_device_idx -= 1
        self._current_device = self._assigned_devices[self._current_device_idx]
        try:
            self.song().view.select_device(self._current_device)
        except Exception:
            pass
        self._attach_parameter_listeners()
        self._reset_encoder_sync_state()
        self._sync_hardware_encoders()
        self._send_active_device_info()
        self._send_parameters_info()
        self._broadcast_selected_device()
        self._update_knob_leds()
        self._update_nav_leds()
        self._update_screen_display()

    def _nav_device_next(self):
        """Sélectionne le plugin +1 de la piste actuelle (s'il existe, sans boucler)"""
        if not self._assigned_devices or self._current_device_idx >= len(self._assigned_devices) - 1:
            self._update_nav_leds()
            return
        self._current_device_idx += 1
        self._current_device = self._assigned_devices[self._current_device_idx]
        try:
            self.song().view.select_device(self._current_device)
        except Exception:
            pass
        self._attach_parameter_listeners()
        self._reset_encoder_sync_state()
        self._sync_hardware_encoders()
        self._send_active_device_info()
        self._send_parameters_info()
        self._broadcast_selected_device()
        self._update_knob_leds()
        self._update_nav_leds()
        self._update_screen_display()

    def _attach_parameter_listeners(self):
        self._remove_parameter_listeners()
        if not self._current_device:
            return
        params = self._current_device.parameters[1:NUM_ENCODERS+1]
        for idx, p in enumerate(params):
            if not p.value_has_listener(self._on_parameter_value_changed):
                p.add_value_listener(self._on_parameter_value_changed)
                self._observed_params.append(p)

    def _remove_parameter_listeners(self):
        for p in self._observed_params:
            try:
                if p and p.value_has_listener(self._on_parameter_value_changed):
                    p.remove_value_listener(self._on_parameter_value_changed)
            except Exception:
                pass
        self._observed_params = []

    def _on_parameter_value_changed(self):
        self._send_parameters_info()
        self._broadcast_all_parameters()
        if not getattr(self, '_updating_from_hardware', False):
            self._sync_hardware_encoders()

    def _reset_encoder_sync_state(self):
        """Réinitialise l'état anti-saut des 24 encodeurs lors d'un changement de piste ou de plugin"""
        self._encoder_synced = [False] * NUM_ENCODERS
        self._encoder_last_raw = [None] * NUM_ENCODERS

    def _sync_hardware_encoders(self):
        """Envoie la position actuelle (0..127) des 24 paramètres au Launch Control XL 3 (Canal 16, CC 13..36).
        Selon le Guide du Programmeur LCXL3 (Page 10) :
        'By default encoders are in absolute mode and provide standard CCs.
         If the DAW sends them position information, they automatically pick that up.'"""
        try:
            dev = self._current_device
            params = dev.parameters[1:NUM_ENCODERS+1] if dev else []
            for idx in range(NUM_ENCODERS):
                cc_num = 13 + idx
                if idx < len(params):
                    p = params[idx]
                    v_range = max(0.0001, (p.max - p.min))
                    val_7bit = int(round((p.value - p.min) / v_range * 127.0))
                    val_7bit = max(0, min(127, val_7bit))
                else:
                    val_7bit = 0
                self._send_midi_all((0xBF, cc_num, val_7bit))
        except Exception as e:
            self.log_message("LivePilot : Erreur dans _sync_hardware_encoders : %s" % str(e))

    def _set_encoder_value(self, encoder_idx, cc_val):
        """Met à jour un paramètre depuis un potentiomètre physique du Launch Control XL 3 sans jamais repartir de zéro"""
        if not self._current_device or encoder_idx >= NUM_ENCODERS:
            return
        params = self._current_device.parameters[1:NUM_ENCODERS+1]
        if encoder_idx >= len(params):
            return

        p = params[encoder_idx]
        v_range = max(0.0001, (p.max - p.min))
        cur_norm = (p.value - p.min) / v_range
        cur_7bit = max(0, min(127, int(round(cur_norm * 127.0))))

        if isinstance(cc_val, float) and 0.0 <= cc_val <= 1.0 and cc_val not in (0, 1):
            raw_cc = int(round(cc_val * 127.0))
        else:
            raw_cc = int(cc_val)
        raw_cc = max(0, min(127, raw_cc))

        if not hasattr(self, '_encoder_synced') or len(self._encoder_synced) != NUM_ENCODERS:
            self._reset_encoder_sync_state()

        last_raw = self._encoder_last_raw[encoder_idx]
        self._encoder_last_raw[encoder_idx] = raw_cc

        # Protection anti-saut à la première manipulation du knob :
        # Si la valeur envoyée par le contrôleur est éloignée de la valeur actuelle du plugin (ex: repart de 0),
        # on applique uniquement le déplacement relatif (+/- pas) à partir de la valeur actuelle du plugin
        # et on synchronise immédiatement le registre interne du potentiomètre sur le Launch Control XL 3.
        if not self._encoder_synced[encoder_idx] and abs(raw_cc - cur_7bit) > 4:
            if last_raw is not None:
                delta = raw_cc - last_raw
                if delta == 0:
                    delta = -1 if raw_cc == 0 else (1 if raw_cc == 127 else 0)
                delta = max(-4, min(4, delta))
            else:
                if raw_cc == 0:
                    delta = -1
                elif raw_cc <= 5 and cur_7bit > 8:
                    delta = max(1, raw_cc)
                elif raw_cc >= 122 and cur_7bit < 119:
                    delta = min(-1, raw_cc - 127)
                else:
                    delta = 1 if raw_cc > cur_7bit else -1

            target_7bit = max(0, min(127, cur_7bit + delta))
            # Synchronise immédiatement le registre matériel du knob sur le Launch Control XL 3
            self._send_midi_all((0xBF, 13 + encoder_idx, target_7bit))
        else:
            self._encoder_synced[encoder_idx] = True
            target_7bit = raw_cc

        norm_val = target_7bit / 127.0
        self._updating_from_hardware = True
        try:
            p.value = max(p.min, min(p.max, p.min + (norm_val * v_range)))
        finally:
            self._updating_from_hardware = False

        if self._web_server:
            self._web_server.broadcast({
                'type': 'param_value',
                'data': {
                    'index': encoder_idx,
                    'value': round(norm_val, 3),
                    'str': str(p)[:12]
                }
            })

    def _adjust_parameter(self, encoder_idx, rel_value):
        if not self._current_device or encoder_idx >= NUM_ENCODERS:
            return
        params = self._current_device.parameters[1:NUM_ENCODERS+1]
        if encoder_idx < len(params):
            p = params[encoder_idx]
            v_range = max(0.0001, (p.max - p.min))
            step = v_range / 127.0
            new_val = max(p.min, min(p.max, p.value + (rel_value * step)))
            self._updating_from_hardware = True
            try:
                p.value = new_val
            finally:
                self._updating_from_hardware = False
            norm_val = (new_val - p.min) / v_range
            val_7bit = max(0, min(127, int(round(norm_val * 127.0))))
            self._send_midi_all((0xBF, 13 + encoder_idx, val_7bit))
            if self._web_server:
                self._web_server.broadcast({
                    'type': 'param_value',
                    'data': {
                        'index': encoder_idx,
                        'value': round(norm_val, 3),
                        'str': str(p)[:12]
                    }
                })

    # =========================================================================
    # NAVIGATION DE BANQUES & PISTES
    # =========================================================================
    def _nav_bank_prev(self):
        if self._current_bank_index > 0:
            self._current_bank_index -= 1
            self._pad_led_cache = [None] * NUM_TRACKS_PER_BANK
            self._send_bank_info()
            self._send_bank_colors()
            self._broadcast_full_sync()
            self._update_pad_leds(force=True)
            self._update_nav_leds()

    def _nav_bank_next(self):
        total_tracks = len(self.song().tracks)
        total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
        if self._current_bank_index < total_banks - 1:
            self._current_bank_index += 1
            self._pad_led_cache = [None] * NUM_TRACKS_PER_BANK
            self._send_bank_info()
            self._send_bank_colors()
            self._broadcast_full_sync()
            self._update_pad_leds(force=True)
            self._update_nav_leds()

    def _select_prev_track(self):
        tracks = list(self.song().tracks)
        if not tracks:
            return
        cur_track = self.song().view.selected_track
        idx = tracks.index(cur_track) if cur_track in tracks else 0
        if idx > 0:
            self.song().view.selected_track = tracks[idx - 1]
        else:
            self._update_pad_leds()
            self._update_nav_leds()

    def _select_next_track(self):
        tracks = list(self.song().tracks)
        if not tracks:
            return
        cur_track = self.song().view.selected_track
        idx = tracks.index(cur_track) if cur_track in tracks else 0
        if idx < len(tracks) - 1:
            self.song().view.selected_track = tracks[idx + 1]
        else:
            self._update_pad_leds()
            self._update_nav_leds()

    def _get_all_groups(self):
        return [t for t in self.song().tracks if getattr(t, 'is_foldable', False)]

    def _nav_group_prev(self):
        groups = self._get_all_groups()
        if not groups:
            return
        tracks = list(self.song().tracks)
        current_idx = tracks.index(self._current_track) if self._current_track in tracks else 0
        prev_group = None
        for g in reversed(groups):
            if tracks.index(g) < current_idx:
                prev_group = g
                break
        if not prev_group:
            prev_group = groups[-1]
        self._select_and_ensure_bank_visible(prev_group)

    def _nav_group_next(self):
        groups = self._get_all_groups()
        if not groups:
            return
        tracks = list(self.song().tracks)
        current_idx = tracks.index(self._current_track) if self._current_track in tracks else -1
        next_group = None
        for g in groups:
            if tracks.index(g) > current_idx:
                next_group = g
                break
        if not next_group:
            next_group = groups[0]
        self._select_and_ensure_bank_visible(next_group)

    def _select_and_ensure_bank_visible(self, target_track):
        tracks = list(self.song().tracks)
        if target_track in tracks:
            idx = tracks.index(target_track)
            target_bank = idx // NUM_TRACKS_PER_BANK
            if target_bank != self._current_bank_index:
                self._current_bank_index = target_bank
                self._pad_led_cache = [None] * NUM_TRACKS_PER_BANK
                self._send_bank_info()
                self._send_bank_colors()
            self.song().view.selected_track = target_track

    def _select_track_in_bank(self, index_in_bank):
        track_idx = (self._current_bank_index * NUM_TRACKS_PER_BANK) + index_in_bank
        tracks = self.song().tracks
        if 0 <= track_idx < len(tracks):
            target_track = tracks[track_idx]
            self.log_message("LivePilot : Selection de la piste %d (%s)" % (track_idx + 1, target_track.name))
            if target_track == self.song().view.selected_track:
                self._update_pad_leds(force_pad_idx=index_in_bank)
                self._update_nav_leds()
            else:
                # Modifier selected_track déclenche automatiquement _on_selected_track_changed()
                self.song().view.selected_track = target_track
                self._update_pad_leds(force_pad_idx=index_in_bank)
        else:
            self.log_message("LivePilot : Piste demandee hors limites (index=%d, total=%d)" % (track_idx, len(tracks)))
            self._update_pad_leds(force_pad_idx=index_in_bank)

    # =========================================================================
    # DIFFUSION WEBSOCKET (Ableton -> Tablette Android)
    # =========================================================================
    def _safe_get_arm(self, track):
        """Lit l'état Arm d'une piste en toute sécurité (les pistes Group, Return et Main n'ont pas d'état Arm
        dans Ableton Live et lèvent RuntimeError si on accède à track.arm)."""
        if not track:
            return False
        try:
            if getattr(track, 'is_foldable', False):
                return False
            if not getattr(track, 'can_be_armed', False):
                return False
            return bool(track.arm)
        except Exception:
            return False

    def _safe_toggle_arm(self, track):
        """Inverse l'état Arm d'une piste uniquement si elle peut être armée (ignore les pistes Group/Return/Main)"""
        if not track:
            return
        try:
            if getattr(track, 'is_foldable', False):
                return
            if not getattr(track, 'can_be_armed', False):
                return
            track.arm = not track.arm
        except Exception:
            pass

    def _build_track_dict(self, track, global_index, active_scene_idx=None):
        if not track:
            return None
        try:
            vol_str = str(track.mixer_device.volume) if (hasattr(track, 'mixer_device') and track.mixer_device) else '0 dB'
        except Exception:
            vol_str = '0 dB'
        try:
            pan_str = str(track.mixer_device.panning) if (hasattr(track, 'mixer_device') and track.mixer_device) else 'C'
            pan_val = round(float(track.mixer_device.panning.value), 2) if (hasattr(track, 'mixer_device') and track.mixer_device and hasattr(track.mixer_device, 'panning')) else 0.0
        except Exception:
            pan_str = 'C'
            pan_val = 0.0

        try:
            is_group = bool(getattr(track, 'is_foldable', False))
        except Exception:
            is_group = False
        try:
            fold_state = bool(getattr(track, 'fold_state', False)) if is_group else False
        except Exception:
            fold_state = False
        try:
            is_grouped = bool(getattr(track, 'is_grouped', False))
            group_name = str(track.group_track.name) if (is_grouped and getattr(track, 'group_track', None)) else ""
        except Exception:
            is_grouped = False
            group_name = ""

        if active_scene_idx is None:
            active_scene_idx = self._get_active_scene_index()

        has_clip = False
        clip_name = ""
        clip_color = ""
        clip_is_playing = False
        clip_is_triggered = False

        try:
            if hasattr(track, 'clip_slots') and track.clip_slots:
                clip_slots = track.clip_slots
                if 0 <= active_scene_idx < len(clip_slots):
                    slot = clip_slots[active_scene_idx]
                    if getattr(slot, 'has_clip', False) and getattr(slot, 'clip', None):
                        has_clip = True
                        clip = slot.clip
                        clip_name = str(getattr(clip, 'name', '') or '')
                        clip_color = int_to_hex_color(getattr(clip, 'color', None))
                        clip_is_playing = bool(getattr(clip, 'is_playing', False))
                        clip_is_triggered = bool(getattr(clip, 'is_triggered', False))
        except Exception:
            pass

        try:
            playing_slot_idx = int(getattr(track, 'playing_slot_index', -1))
        except Exception:
            playing_slot_idx = -1
        is_track_playing = (playing_slot_idx >= 0)
        if is_track_playing and has_clip and playing_slot_idx == active_scene_idx:
            clip_is_playing = True

        try:
            t_name = str(getattr(track, 'name', '') or ('Track %d' % (global_index + 1)))
        except Exception:
            t_name = 'Track %d' % (global_index + 1)

        try:
            t_color = int_to_hex_color(getattr(track, 'color', None))
        except Exception:
            t_color = '#444b60'

        try:
            t_mute = bool(getattr(track, 'mute', False))
        except Exception:
            t_mute = False

        try:
            t_solo = bool(getattr(track, 'solo', False))
        except Exception:
            t_solo = False

        return {
            'index': global_index,
            'name': t_name,
            'color': t_color,
            'is_group': is_group,
            'fold_state': fold_state,
            'is_grouped': is_grouped,
            'group_name': group_name,
            'mute': t_mute,
            'solo': t_solo,
            'arm': self._safe_get_arm(track),
            'vol_str': vol_str,
            'pan_str': pan_str,
            'pan_val': pan_val,
            'has_clip': has_clip,
            'clip_name': clip_name,
            'clip_color': clip_color,
            'clip_is_playing': clip_is_playing,
            'clip_is_triggered': clip_is_triggered,
            'is_track_playing': is_track_playing
        }

    def _build_params_list(self):
        params_out = []
        if not self._current_device:
            for i in range(NUM_ENCODERS):
                params_out.append({'index': i, 'name': '-', 'value': 0.0, 'str': '-', 'is_assigned': False})
            return params_out

        dev_params = self._current_device.parameters[1:NUM_ENCODERS+1]
        for i in range(NUM_ENCODERS):
            if i < len(dev_params):
                p = dev_params[i]
                v_range = max(0.0001, (p.max - p.min))
                norm_val = round((p.value - p.min) / v_range, 3)
                params_out.append({
                    'index': i,
                    'name': p.name[:14],
                    'value': norm_val,
                    'str': str(p)[:10],
                    'is_assigned': True
                })
            else:
                params_out.append({'index': i, 'name': '-', 'value': 0.0, 'str': '-', 'is_assigned': False})
        return params_out

    def _get_active_scene_info(self):
        song = self.song()
        active_sc = None
        scene_idx = 0
        for idx, sc in enumerate(song.scenes):
            if getattr(sc, 'is_playing', False):
                active_sc = sc
                scene_idx = idx
                break
        if not active_sc:
            active_sc = song.view.selected_scene
            try:
                scene_idx = list(song.scenes).index(active_sc)
            except Exception:
                scene_idx = 0

        total_sc = len(song.scenes)
        sc_name = active_sc.name if (active_sc and active_sc.name) else ("Scene %d" % (scene_idx + 1))
        sig_num = getattr(song, 'signature_numerator', 4)
        sig_den = getattr(song, 'signature_denominator', 4)
        tempo = round(float(song.tempo), 1)
        
        # Ligne 2 : Scène suivante (repère live de transition)
        next_sc_idx = scene_idx + 1
        if next_sc_idx < total_sc:
            next_sc = song.scenes[next_sc_idx]
            next_sc_name = next_sc.name if (next_sc and next_sc.name) else ("Scene %d" % (next_sc_idx + 1))
            next_sc_color = int_to_hex_color(getattr(next_sc, 'color', None))
            next_sc_num = next_sc_idx + 1
        else:
            next_sc_name = "--- (FIN DU LIVE / DERNIÈRE SCÈNE) ---"
            next_sc_color = "#333b4f"
            next_sc_num = 0

        desc_line = "Scène %d / %d  •  Tempo: %.1f BPM  •  Signature: %d/%d  •  Session Live" % (
            scene_idx + 1, total_sc, tempo, sig_num, sig_den
        )

        # Scène précédente (carte de gauche du bandeau)
        prev_sc_idx = scene_idx - 1
        if prev_sc_idx >= 0:
            prev_sc = song.scenes[prev_sc_idx]
            prev_sc_name = prev_sc.name if (prev_sc and prev_sc.name) else ("Scene %d" % (prev_sc_idx + 1))
            prev_sc_num = prev_sc_idx + 1
        else:
            prev_sc_name = "--- DÉBUT DU LIVE ---"
            prev_sc_num = 0

        return {
            'num': scene_idx + 1,
            'total': total_sc,
            'name': sc_name,
            'desc': desc_line,
            'color': int_to_hex_color(getattr(active_sc, 'color', None)) if active_sc else '#1e2230',
            'is_playing': bool(song.is_playing),
            'next_num': next_sc_num,
            'next_name': next_sc_name,
            'next_color': next_sc_color,
            'prev_num': prev_sc_num,
            'prev_name': prev_sc_name,
            'signature': "%d/%d" % (sig_num, sig_den)
        }

    def _get_play_status_string(self):
        song = self.song()
        if song.is_playing:
            return 'PLAY'
        cur_time = float(getattr(song, 'current_song_time', 0.0))
        if cur_time > 0.05:
            return 'PAUSE'
        return 'STOP'

    def _broadcast_full_sync(self):
        if not self._web_server:
            return
        try:
            song = self.song()
            tracks = song.tracks
            total_tracks = len(tracks)
            total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)

            # 16 pistes de la banque courante (miroir des 16 boutons du Launch Control XL)
            bank_tracks = []
            active_sc_idx = self._get_active_scene_index()
            start_idx = self._current_bank_index * NUM_TRACKS_PER_BANK
            for i in range(NUM_TRACKS_PER_BANK):
                t_idx = start_idx + i
                if t_idx < total_tracks:
                    bank_tracks.append(self._build_track_dict(tracks[t_idx], t_idx, active_sc_idx))
                else:
                    bank_tracks.append(None)

            # Liste de toutes les scènes
            scenes_list = []
            for idx, sc in enumerate(song.scenes):
                scenes_list.append({
                    'index': idx,
                    'name': sc.name or ("Scene %d" % (idx + 1)),
                    'color': int_to_hex_color(getattr(sc, 'color', None)),
                    'is_playing': bool(getattr(sc, 'is_playing', False))
                })

            # Données de scène active sur 2 lignes
            active_scene_data = self._get_active_scene_info()

            # Chaîne des devices avec numérotation [1/3], [2/3]...
            devs_data = []
            total_devs = len(self._assigned_devices)
            if self._current_track:
                for idx, dev in enumerate(self._assigned_devices):
                    devs_data.append({
                        'index': idx,
                        'num': idx + 1,
                        'total': total_devs,
                        'name': dev.name,
                        'maker': str(getattr(dev, 'class_display_name', '') or ''),
                        'label': "[%d/%d] %s" % (idx + 1, total_devs, dev.name)
                    })

            active_dev_label = "[%d/%d] %s" % (self._current_device_idx + 1, total_devs, self._current_device.name) if self._current_device else "No Assignment"

            cur_time = str(song.current_song_time) if hasattr(song, 'current_song_time') else '1.1.1'

            try:
                sel_track_idx = list(tracks).index(self._current_track) if self._current_track in tracks else 0
            except ValueError:
                sel_track_idx = 0

            m_vol = song.master_track.mixer_device.volume if (hasattr(song, 'master_track') and song.master_track) else None
            m_vol_val = round(float(m_vol.value), 3) if m_vol else 0.85
            m_vol_str = str(m_vol) if m_vol else '0.0 dB'

            payload = {
                'version': LIVEPILOT_VERSION,
                'tempo': round(float(song.tempo), 1),
                'is_playing': bool(song.is_playing),
                'play_status': self._get_play_status_string(),
                'position': cur_time,
                'master_volume': {'value': m_vol_val, 'str': m_vol_str},
                'active_scene': active_scene_data,
                'scenes': scenes_list,
                'bank_index': self._current_bank_index,
                'total_banks': total_banks,
                'selected_track_index': sel_track_idx,
                'tracks': bank_tracks,
                'devices': devs_data,
                'active_device_index': self._current_device_idx,
                'active_device_name': active_dev_label,
                'parameters': self._build_params_list(),
                'midi_config': getattr(self, '_midi_config', {})
            }
            self._web_server.broadcast({'type': 'full_sync', 'data': payload})
        except Exception as e:
            self.log_message("LivePilot : Erreur dans _broadcast_full_sync : %s" % str(e))

    def _broadcast_transport(self):
        if not self._web_server:
            return
        song = self.song()
        self._web_server.broadcast({
            'type': 'transport',
            'data': {
                'tempo': round(float(song.tempo), 1),
                'is_playing': bool(song.is_playing),
                'play_status': self._get_play_status_string(),
                'position': str(song.current_song_time) if hasattr(song, 'current_song_time') else '1.1.1'
            }
        })

    def _broadcast_active_scene(self):
        if not self._web_server:
            return
        self._web_server.broadcast({
            'type': 'scene',
            'data': self._get_active_scene_info()
        })

    def _broadcast_selected_track(self):
        if not self._web_server:
            return
        try:
            tracks = list(self.song().tracks)
            total_tracks = len(tracks)
            total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
            try:
                sel_idx = tracks.index(self._current_track) if self._current_track in tracks else 0
            except ValueError:
                sel_idx = 0

            bank_tracks = []
            active_sc_idx = self._get_active_scene_index()
            start_idx = self._current_bank_index * NUM_TRACKS_PER_BANK
            for i in range(NUM_TRACKS_PER_BANK):
                t_idx = start_idx + i
                if t_idx < len(tracks):
                    bank_tracks.append(self._build_track_dict(tracks[t_idx], t_idx, active_sc_idx))
                else:
                    bank_tracks.append(None)

            total_devs = len(self._assigned_devices)
            devs_data = []
            for idx, dev in enumerate(self._assigned_devices):
                devs_data.append({
                    'index': idx,
                    'num': idx + 1,
                    'total': total_devs,
                    'name': dev.name,
                    'maker': str(getattr(dev, 'class_display_name', '') or ''),
                    'label': "[%d/%d] %s" % (idx + 1, total_devs, dev.name)
                })

            active_dev_label = "[%d/%d] %s" % (self._current_device_idx + 1, total_devs, self._current_device.name) if self._current_device else "No Assignment"

            self._web_server.broadcast({
                'type': 'track_selected',
                'data': {
                    'track_index': sel_idx,
                    'bank_index': self._current_bank_index,
                    'total_banks': total_banks,
                    'tracks': bank_tracks,
                    'devices': devs_data,
                    'active_device_name': active_dev_label,
                    'active_device_index': self._current_device_idx,
                    'parameters': self._build_params_list()
                }
            })
        except Exception as e:
            self.log_message("LivePilot : Erreur dans _broadcast_selected_track : %s" % str(e))

    def _broadcast_selected_device(self):
        if not self._web_server:
            return
        total_devs = len(self._assigned_devices)
        active_dev_label = "[%d/%d] %s" % (self._current_device_idx + 1, total_devs, self._current_device.name) if self._current_device else "No Assignment"
        self._web_server.broadcast({
            'type': 'device_selected',
            'data': {
                'device_index': self._current_device_idx,
                'device_name': active_dev_label,
                'parameters': self._build_params_list()
            }
        })

    def _broadcast_all_parameters(self):
        if not self._web_server:
            return
        if not self._current_device:
            return
        dev_params = self._current_device.parameters[1:NUM_ENCODERS+1]
        for idx in range(min(NUM_ENCODERS, len(dev_params))):
            p = dev_params[idx]
            v_range = max(0.0001, (p.max - p.min))
            norm_val = round((p.value - p.min) / v_range, 3)
            self._web_server.broadcast({
                'type': 'param_value',
                'data': {
                    'index': idx,
                    'value': norm_val,
                    'str': str(p)[:10]
                }
            })

    # =========================================================================
    # POLLING TEMPS RÉEL DES VU-MÈTRES (25 FPS)
    # =========================================================================
    def _schedule_meter_poll(self):
        self._poll_meters()

    def _poll_meters(self):
        try:
            if self._web_server and len(self._web_server.clients) > 0:
                tracks = self.song().tracks
                start_idx = self._current_bank_index * NUM_TRACKS_PER_BANK
                meters_list = []
                for i in range(NUM_TRACKS_PER_BANK):
                    t_idx = start_idx + i
                    if t_idx < len(tracks):
                        t = tracks[t_idx]
                        try:
                            l = float(getattr(t, 'output_meter_left', 0.0))
                            r = float(getattr(t, 'output_meter_right', 0.0))
                        except Exception:
                            l, r = 0.0, 0.0
                        meters_list.append({'left': round(l, 3), 'right': round(r, 3)})
                    else:
                        meters_list.append({'left': 0.0, 'right': 0.0})
                self._web_server.broadcast({'type': 'meters', 'data': meters_list})
        except Exception:
            pass
        # Reprogramme l'appel toutes les ~40ms (25 Hz)
        self.schedule_message(2, self._poll_meters)

    # =========================================================================
    # GESTION DES COMMANDES REÇUES DE LA TABLETTE (Tablette -> Ableton)
    # =========================================================================
    def _on_web_client_message(self, msg):
        """Reçu dans le thread WebSocket, redirigé sur le thread principal Ableton"""
        self.schedule_message(0, lambda: self._process_client_action(msg))

    def _process_client_action(self, msg):
        action = msg.get('action')
        if not action:
            return

        if action == 'request_full_sync':
            self._broadcast_full_sync()
            self._update_pad_leds(force=True)
            self._update_knob_leds(force=True)
            self._update_nav_leds()

        elif action == 'select_track':
            t_idx = msg.get('track_index', 0)
            tracks = list(self.song().tracks)
            if 0 <= t_idx < len(tracks):
                target = tracks[t_idx]
                if self.song().view.selected_track != target:
                    # Déclenche automatiquement _on_selected_track_changed()
                    self.song().view.selected_track = target
                else:
                    self._update_pad_leds()
                    self._update_knob_leds()
                    self._update_nav_leds()

        elif action == 'select_device':
            d_idx = msg.get('device_index', 0)
            if 0 <= d_idx < len(self._assigned_devices):
                self._current_device_idx = d_idx
                self._current_device = self._assigned_devices[d_idx]
                try:
                    self.song().view.select_device(self._current_device)
                except Exception:
                    pass
                self._attach_parameter_listeners()
                self._reset_encoder_sync_state()
                self._sync_hardware_encoders()
                self._send_active_device_info()
                self._send_parameters_info()
                self._broadcast_selected_device()
                self._update_knob_leds()
                self._update_nav_leds()
                self._update_screen_display()

        elif action == 'select_relative_device':
            offset = int(msg.get('offset', 1))
            new_idx = self._current_device_idx + offset
            if 0 <= new_idx < len(self._assigned_devices):
                self._current_device_idx = new_idx
                self._current_device = self._assigned_devices[new_idx]
                try:
                    self.song().view.select_device(self._current_device)
                except Exception:
                    pass
                self._attach_parameter_listeners()
                self._reset_encoder_sync_state()
                self._sync_hardware_encoders()
                self._send_active_device_info()
                self._send_parameters_info()
                self._broadcast_selected_device()
                self._update_knob_leds()
                self._update_nav_leds()
                self._update_screen_display()

        elif action == 'set_parameter':
            p_idx = msg.get('index', 0)
            norm_val = msg.get('value', 0.0)
            if self._current_device:
                params = self._current_device.parameters[1:NUM_ENCODERS+1]
                if 0 <= p_idx < len(params):
                    p = params[p_idx]
                    p.value = p.min + norm_val * (p.max - p.min)
                    val_7bit = max(0, min(127, int(round(norm_val * 127.0))))
                    self._send_midi_all((0xBF, 13 + p_idx, val_7bit))

        elif action == 'trigger_scene':
            sc_idx = msg.get('scene_index', 0)
            scenes = list(self.song().scenes)
            if 0 <= sc_idx < len(scenes):
                scenes[sc_idx].fire()
                self._broadcast_active_scene()
                self._broadcast_selected_track()

        elif action == 'toggle_play':
            self.song().is_playing = not self.song().is_playing

        elif action == 'adjust_tempo':
            delta = msg.get('delta', 0.0)
            new_tempo = max(20.0, min(999.0, self.song().tempo + delta))
            self.song().tempo = new_tempo

        elif action == 'set_master_volume':
            v = float(msg.get('value', 0.85))
            if hasattr(self.song(), 'master_track') and self.song().master_track:
                self.song().master_track.mixer_device.volume.value = max(0.0, min(1.0, v))

        elif action == 'set_track_pan':
            t_idx = msg.get('track_index', 0)
            p_val = float(msg.get('value', 0.0))
            tracks = list(self.song().tracks)
            if 0 <= t_idx < len(tracks) and hasattr(tracks[t_idx], 'mixer_device'):
                tracks[t_idx].mixer_device.panning.value = max(-1.0, min(1.0, p_val))
                self._broadcast_selected_track()

        elif action in ('select_bank', 'switch_bank'):
            b_idx = int(msg.get('bank_index', msg.get('bank', 0)))
            tracks = self.song().tracks
            total_banks = max(1, (len(tracks) + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
            self._current_bank_index = max(0, min(total_banks - 1, b_idx))
            self._send_bank_info()
            self._send_bank_colors()
            self._broadcast_full_sync()

        elif action == 'nav_bank_prev':
            self._nav_bank_prev()

        elif action == 'nav_bank_next':
            self._nav_bank_next()

        elif action == 'nav_device_prev':
            self._nav_device_prev()

        elif action == 'nav_device_next':
            self._nav_device_next()

        elif action == 'set_auto_follow':
            self._auto_follow = bool(msg.get('value', True))
            if self._auto_follow:
                self._on_selected_track_changed()

        elif action == 'fire_relative_scene':
            # Flèches du bandeau de scènes : -1 = précédente, +1 = suivante
            delta = int(msg.get('delta', 1))
            info = self._get_active_scene_info()
            scenes = list(self.song().scenes)
            target = (info.get('num', 1) - 1) + delta
            if 0 <= target < len(scenes):
                scenes[target].fire()
                self.song().view.selected_scene = scenes[target]
                self._broadcast_active_scene()
                self._broadcast_selected_track()

        elif action in ('toggle_mute', 'toggle_solo', 'toggle_arm'):
            t_idx = msg.get('track_index', 0)
            tracks = list(self.song().tracks)
            if 0 <= t_idx < len(tracks):
                t = tracks[t_idx]
                try:
                    if action == 'toggle_mute':
                        t.mute = not t.mute
                    elif action == 'toggle_solo':
                        t.solo = not t.solo
                    elif action == 'toggle_arm':
                        self._safe_toggle_arm(t)
                except Exception:
                    pass
                self._broadcast_selected_track()

        elif action == 'save_midi_config':
            cfg = msg.get('config', {})
            if cfg and isinstance(cfg, dict):
                self._midi_config.update(cfg)
                if 'nav_buttons' not in self._midi_config or not isinstance(self._midi_config['nav_buttons'], dict):
                    self._midi_config['nav_buttons'] = copy.deepcopy(DEFAULT_NAV_BUTTONS)
                self._save_midi_config_to_disk()
                self.log_message("LivePilot : Configuration MIDI mise a jour : %s" % str(self._midi_config))
                self._broadcast_full_sync()
                self._update_pad_leds()
                self._update_nav_leds()

    def _get_midi_config_path(self):
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'midi_config.json')

    def _load_midi_config_from_disk(self):
        try:
            cfg_path = self._get_midi_config_path()
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                if isinstance(loaded, dict):
                    self._midi_config.update(loaded)
                    if 'nav_buttons' not in self._midi_config or not isinstance(self._midi_config['nav_buttons'], dict):
                        self._midi_config['nav_buttons'] = copy.deepcopy(DEFAULT_NAV_BUTTONS)
                    else:
                        for k, v in DEFAULT_NAV_BUTTONS.items():
                            if k not in self._midi_config['nav_buttons']:
                                self._midi_config['nav_buttons'][k] = copy.deepcopy(v)
                    # Migration auto vers v1.2.0 : Track ◄ = device_prev, Track ► = device_next
                    if self._midi_config.get('schema_version') != LIVEPILOT_VERSION:
                        self._midi_config['schema_version'] = LIVEPILOT_VERSION
                        self._midi_config['nav_buttons']['track_left']['action'] = 'device_prev'
                        self._midi_config['nav_buttons']['track_right']['action'] = 'device_next'
                        self._save_midi_config_to_disk()
                    self.log_message("LivePilot : Configuration MIDI chargee depuis midi_config.json")
        except Exception as e:
            self.log_message("LivePilot : Erreur chargement midi_config.json : %s" % str(e))

    def _save_midi_config_to_disk(self):
        try:
            cfg_path = self._get_midi_config_path()
            with open(cfg_path, 'w', encoding='utf-8') as f:
                json.dump(self._midi_config, f, indent=2)
        except Exception as e:
            self.log_message("LivePilot : Erreur sauvegarde midi_config.json : %s" % str(e))

    def _execute_nav_action(self, action_name, btn_label=""):
        """Exécute l'action configurée par l'utilisateur pour un bouton Page ▲/▼ ou Track ◄/►"""
        self.log_message("LivePilot : Execution action '%s' (bouton %s)" % (action_name, btn_label))
        if action_name == 'track_prev':
            self._select_prev_track()
        elif action_name == 'track_next':
            self._select_next_track()
        elif action_name == 'bank_prev':
            self._nav_bank_prev()
        elif action_name == 'bank_next':
            self._nav_bank_next()
        elif action_name == 'device_prev':
            self._nav_device_prev()
        elif action_name == 'device_next':
            self._nav_device_next()
        elif action_name == 'scene_prev':
            self._nav_screen_left()
        elif action_name == 'scene_next':
            self._nav_screen_right()
        elif action_name == 'scene_fire_selected':
            self._on_btn_valid_pressed()
        elif action_name in ('scene_fire_next', 'scene_fire_prev'):
            delta = 1 if action_name == 'scene_fire_next' else -1
            info = self._get_active_scene_info()
            scenes = list(self.song().scenes)
            target = (info.get('num', 1) - 1) + delta
            if 0 <= target < len(scenes):
                scenes[target].fire()
                self.song().view.selected_scene = scenes[target]
                self._send_scene_info()
                self._broadcast_active_scene()
                self._broadcast_selected_track()
        elif action_name == 'group_prev':
            self._nav_group_prev()
        elif action_name == 'group_next':
            self._nav_group_next()
        elif action_name == 'play_toggle':
            self.song().is_playing = not self.song().is_playing
            self._update_nav_leds()
            self._broadcast_transport()
        elif action_name == 'mute_selected':
            if self._current_track and hasattr(self._current_track, 'mute'):
                self._current_track.mute = not self._current_track.mute
                self._broadcast_selected_track()
        elif action_name == 'solo_selected':
            if self._current_track and hasattr(self._current_track, 'solo'):
                self._current_track.solo = not self._current_track.solo
                self._broadcast_selected_track()
        elif action_name == 'arm_selected':
            if self._current_track:
                self._safe_toggle_arm(self._current_track)
                self._broadcast_selected_track()
        self._update_nav_leds()

    # =========================================================================
    # COMPATIBILITÉ MIDI / SYSEX (Launch Control XL MK3 / MK2)
    # =========================================================================
    def build_midi_map(self, midi_map_handle):
        """
        Enregistre auprès du moteur C++ d'Ableton Live le forwarding de TOUS les CCs et Notes.
        Sans cette méthode, Ableton filtre et bloque tous les messages CC et Note en interne
        et n'appelle JAMAIS receive_midi() !
        """
        super(LivePilot16, self).build_midi_map(midi_map_handle)
        if not hasattr(self, '_c_instance') or not self._c_instance:
            return

        handle = self._c_instance.handle()
        self.log_message("LivePilot : Construction du MIDI Map - Forwarding universel...")

        # Enregistrement du forwarding pour TOUS les canaux (0 à 15, soit Canaux 1 à 16)
        for channel in range(16):
            # Forwarder tous les CCs (0..127) : potentiomètres, faders, boutons CC, CC 30 Novation Mode Select
            for cc in range(128):
                try:
                    Live.MidiMap.forward_midi_cc(handle, midi_map_handle, channel, cc)
                except Exception:
                    pass

            # Forwarder toutes les Notes (0..127) : pads, boutons de sélection Note
            for note in range(128):
                try:
                    Live.MidiMap.forward_midi_note(handle, midi_map_handle, channel, note)
                except Exception:
                    pass

        self.log_message("LivePilot : MIDI Map active (Forwarding CC & Notes 100% connecte) !")

    def receive_midi(self, midi_bytes):
        if not midi_bytes:
            return

        # Si cette instance est un compagnon (Port 2), relayer immédiatement le message au Master
        if not self._is_master and LivePilot16._master_instance:
            LivePilot16._master_instance.receive_midi(midi_bytes)
            return

        status = midi_bytes[0]
        msg_type = status & 0xF0
        channel = (status & 0x0F) + 1
        data1 = midi_bytes[1] if len(midi_bytes) > 1 else 0
        data2 = midi_bytes[2] if len(midi_bytes) > 2 else 0

        self.log_message("LivePilot MIDI IN: status=0x%02X ch=%d data1=%d data2=%d" % (status, channel, data1, data2))

        # --- GESTION DES PROGRAM CHANGES (0xC0) ---
        # Certains templates ou modes Novation émettent un Program Change
        if msg_type == 0xC0:
            prog_num = data1
            if self._web_server:
                try:
                    self._web_server.broadcast({
                        'type': 'midi_event',
                        'data': {
                            'status': status,
                            'channel': channel,
                            'type': 'prog_change',
                            'num': prog_num,
                            'val': prog_num
                        }
                    })
                except Exception:
                    pass
            if 0 <= prog_num < NUM_TRACKS_PER_BANK:
                self.log_message("LivePilot : Program Change %d recu -> Selection Piste %d" % (prog_num, prog_num + 1))
                self._select_track_in_bank(prog_num)
                return
            elif 1 <= prog_num <= NUM_TRACKS_PER_BANK:
                self.log_message("LivePilot : Program Change %d recu -> Selection Piste %d" % (prog_num, prog_num))
                self._select_track_in_bank(prog_num - 1)
                return
            super(LivePilot16, self).receive_midi(midi_bytes)
            return

        # S'il manque le 3e octet pour un CC ou Note, passer à la classe parente
        if len(midi_bytes) < 3:
            super(LivePilot16, self).receive_midi(midi_bytes)
            return

        # Diffusion du moniteur MIDI temps réel vers la tablette
        if self._web_server:
            try:
                self._web_server.broadcast({
                    'type': 'midi_event',
                    'data': {
                        'status': status,
                        'channel': channel,
                        'type': 'cc' if msg_type == 0xB0 else ('note_on' if (msg_type == 0x90 and data2 > 0) else 'note_off'),
                        'num': data1,
                        'val': data2
                    }
                })
            except Exception:
                pass

        cfg = getattr(self, '_midi_config', {})
        cfg_knobs = cfg.get('knobs', DEFAULT_KNOB_CCS)
        cfg_buttons = cfg.get('buttons', DEFAULT_BUTTON_CCS)
        btn_type = cfg.get('button_type', 'cc')

        # --- GESTION DES MESSAGES CONTROL CHANGE (CC) ---
        if msg_type == 0xB0:
            cc_num, cc_val = data1, data2

            # 0. GESTION DU MODE DE SURFACE LAUNCH CONTROL XL 3 (Canal 7, CC 30 : 0xB6 0x1E <mode>)
            # En Custom Mode (val >= 6), le firmware Novation désactive matériellement Page ▲/▼ et Track ◄/►.
            # On bascule donc automatiquement la surface en mode DAW Control (02h) où Page, Track, Pads, Knobs et LEDs sont 100% actifs.
            if channel == 7 and cc_num == CC_NOVATION_MODE_SELECT:
                if cc_val in (1, 2):
                    self._lcxl3_surface_mode = 'daw'
                    self.log_message("LivePilot : Surface Launch Control XL 3 en mode DAW (%d) -> Touches Page & Track actives !" % cc_val)
                    self._update_pad_leds()
                    self._update_knob_leds()
                    self._update_nav_leds()
                    self._update_screen_display()
                else:
                    self.log_message("LivePilot : Mode Custom (%d) detecte sur Canal 7 CC 30 -> Bascule auto en DAW Control (02h) pour activer Page & Track !" % cc_val)
                    self._enforce_daw_control_mode()
                    try:
                        self.schedule_message(1, self._enforce_daw_control_mode)
                        self.schedule_message(2, self._update_pad_leds)
                        self.schedule_message(2, self._update_knob_leds)
                        self.schedule_message(2, self._update_nav_leds)
                        self.schedule_message(2, self._update_screen_display)
                    except Exception:
                        pass
                return

            # 1. NAVIGATION MATÉRIELLE CONFIGURABLE (Page ▲/▼, Track ◄/►)
            nav_cfg = cfg.get('nav_buttons', DEFAULT_NAV_BUTTONS)
            matched_nav_key = None
            matched_nav_action = None
            if isinstance(nav_cfg, dict):
                for n_key, n_info in nav_cfg.items():
                    if isinstance(n_info, dict) and n_info.get('type', 'cc') == 'cc' and n_info.get('cc') == cc_num:
                        matched_nav_key = n_key
                        matched_nav_action = n_info.get('action')
                        break

            if not matched_nav_key:
                if cc_num in (CC_NAV_PAGE_UP, 106):
                    matched_nav_key = 'page_up'
                    matched_nav_action = nav_cfg.get('page_up', {}).get('action', 'bank_prev') if isinstance(nav_cfg, dict) else 'bank_prev'
                elif cc_num in (CC_NAV_PAGE_DOWN, 107):
                    matched_nav_key = 'page_down'
                    matched_nav_action = nav_cfg.get('page_down', {}).get('action', 'bank_next') if isinstance(nav_cfg, dict) else 'bank_next'
                elif cc_num in (CC_NAV_TRACK_LEFT, CC_NAV_TRACK_PREV, 103):
                    matched_nav_key = 'track_left'
                    matched_nav_action = nav_cfg.get('track_left', {}).get('action', 'device_prev') if isinstance(nav_cfg, dict) else 'device_prev'
                elif cc_num in (CC_NAV_TRACK_RIGHT, CC_NAV_TRACK_NEXT, 102):
                    matched_nav_key = 'track_right'
                    matched_nav_action = nav_cfg.get('track_right', {}).get('action', 'device_next') if isinstance(nav_cfg, dict) else 'device_next'

            if matched_nav_key:
                if cc_val > 0 and matched_nav_action and matched_nav_action != 'none':
                    self._execute_nav_action(matched_nav_action, matched_nav_key)
                else:
                    self._update_nav_leds()
                return

            # Transport matériel Launch Control XL 3
            if cc_num == CC_HW_PLAY:
                if cc_val > 0:
                    self.song().is_playing = not self.song().is_playing
                self._update_nav_leds()
                return
            elif cc_num == CC_HW_RECORD:
                if cc_val > 0:
                    self.song().record_mode = not self.song().record_mode
                self._update_nav_leds()
                return
            elif cc_num == CC_HW_SOLO_ARM and cc_val > 0:
                if self._current_track:
                    self._safe_toggle_arm(self._current_track)
                return
            elif cc_num == CC_HW_MUTE_SELECT and cc_val > 0:
                if self._current_track and hasattr(self._current_track.mixer_device, 'track_activator'):
                    try:
                        act = self._current_track.mixer_device.track_activator
                        act.value = not act.value
                    except Exception:
                        pass
                return

            # 2. 8 FADERS DE VOLUME
            # Mode DAW Novation : CC 5 à 12 sur canal 16
            # Mode Custom Novation : CC 25 à 32 (DEFAULT_FADER_CCS)
            fader_idx = None
            if 5 <= cc_num <= 12 and channel == 16:
                fader_idx = cc_num - 5
            elif channel != 16 and cc_num in DEFAULT_FADER_CCS:
                fader_idx = DEFAULT_FADER_CCS.index(cc_num)

            if fader_idx is not None and fader_idx < 8:
                trk_idx = self._current_bank_index * NUM_TRACKS_PER_BANK + fader_idx
                tracks = list(self.song().tracks)
                if trk_idx < len(tracks):
                    try:
                        tracks[trk_idx].mixer_device.volume.value = cc_val / 127.0
                    except Exception:
                        pass
                return

            # 3. 24 POTENTIOMÈTRES KNOBS
            # Mode DAW Relatif Novation : CC 77 à 100 sur canal 16 (pivot 64)
            if channel == 16 and 77 <= cc_num <= 100:
                rel_idx = cc_num - 77
                rel_delta = cc_val - 64
                if rel_delta != 0:
                    self._adjust_parameter(rel_idx, rel_delta)
                return

            # Mode DAW Absolu Novation : CC 13 à 36 (sur canal 16)
            # Mode Custom Novation : CC 1 à 24 (sur canal 1)
            knob_idx = None
            if channel == 16 and 13 <= cc_num <= 36:
                knob_idx = cc_num - 13
            elif channel != 16 and cc_num in cfg_knobs:
                knob_idx = cfg_knobs.index(cc_num)
            elif cc_num in cfg_knobs and cc_num not in range(13, 37):
                knob_idx = cfg_knobs.index(cc_num)

            if knob_idx is not None and knob_idx < NUM_ENCODERS:
                self._set_encoder_value(knob_idx, cc_val)
                return

            # 4. GESTION DU RELÂCHEMENT DES PADS (cc_val == 0)
            # Lors du relâchement physique d'un pad, on rafraîchit UNIQUEMENT ce pad spécifique
            # pour ne jamais solliciter ni faire clignoter les 15 autres pads !
            btn_items = cfg.get('button_items', [])
            btn_types = cfg.get('button_types', [])
            if cc_val == 0:
                released_pad_idx = None
                if 37 <= cc_num <= 52:
                    released_pad_idx = cc_num - 37
                elif cc_num in cfg_buttons:
                    idx = cfg_buttons.index(cc_num)
                    if idx < NUM_TRACKS_PER_BANK:
                        released_pad_idx = idx
                elif btn_items:
                    for it in btn_items:
                        if it.get('type') == 'cc' and it.get('num') == cc_num:
                            released_pad_idx = it.get('index', 0)
                            break
                if released_pad_idx is not None:
                    self._update_pad_leds(force_pad_idx=released_pad_idx)
                    return

            # 5. 16 PADS DE SÉLECTION DE PISTES EN MODE DAW (CC 37 à 52 sur Canal 1)
            # Prioritaire pour éviter tout conflit avec les anciens numéros Custom 33..48
            if 37 <= cc_num <= 52 and cc_val > 0 and channel == 1:
                pad_idx = cc_num - 37
                self._select_track_in_bank(pad_idx)
                return

            # 6. PADS APPRIS VIA MIDI LEARN INTERACTIF
            if btn_items and cc_val > 0:
                same_num_items = [it for it in btn_items if it.get('num') == cc_num and it.get('type') == 'cc']
                for item in btn_items:
                    if item.get('type') == 'cc' and item.get('num') == cc_num:
                        it_ch = item.get('channel')
                        if it_ch and it_ch > 0 and channel != it_ch:
                            continue
                        exp_val = item.get('val')
                        if len(same_num_items) > 1 and exp_val is not None:
                            if cc_val != exp_val:
                                continue
                        target_idx = item.get('index', 0)
                        self._select_track_in_bank(target_idx)
                        return

            # 7. AUTRES PADS (DAW autre canal ou Mode Custom CC 33 à 48)
            if 37 <= cc_num <= 52 and cc_val > 0:
                pad_idx = cc_num - 37
                self._select_track_in_bank(pad_idx)
                return

            if cc_num in cfg_buttons and cc_val > 0:
                btn_idx = cfg_buttons.index(cc_num)
                if btn_idx < NUM_TRACKS_PER_BANK:
                    self._select_track_in_bank(btn_idx)
                    return

            # 8. NOVATION SURFACE MODE SELECT (CC 30, ex: Canal 7)
            if cc_num == CC_NOVATION_MODE_SELECT:
                target_trk = None
                if cc_val in NOVATION_MODE_TO_TRACK:
                    target_trk = NOVATION_MODE_TO_TRACK[cc_val]
                elif 1 <= cc_val <= NUM_TRACKS_PER_BANK:
                    target_trk = cc_val - 1
                elif 0 <= cc_val < NUM_TRACKS_PER_BANK:
                    target_trk = cc_val

                if target_trk is not None:
                    self._select_track_in_bank(target_trk)
                    return

            # 9. Navigation additionnelle et Jog
            if cc_num == CC_NAV_GROUP_PREV and cc_val > 0:
                self._nav_group_prev()
                return
            elif cc_num == CC_NAV_GROUP_NEXT and cc_val > 0:
                self._nav_group_next()
                return
            elif cc_num == CC_NAV_DEV_PREV and cc_val > 0:
                self._nav_device_prev()
                return
            elif cc_num == CC_NAV_DEV_NEXT and cc_val > 0:
                self._nav_device_next()
                return
            elif cc_num == CC_ENC17_JOG:
                delta = cc_val if cc_val < 64 else (cc_val - 128)
                self._adjust_master_jog(delta)
                return
            elif cc_num == CC_ENC17_PUSH and cc_val > 0:
                self._toggle_master_mode()
                return
            elif cc_num == CC_NAV_LEFT and cc_val > 0:
                self._nav_screen_left()
                return
            elif cc_num == CC_NAV_RIGHT and cc_val > 0:
                self._nav_screen_right()
                return
            elif cc_num == CC_BTN_VALID and cc_val > 0:
                self._on_btn_valid_pressed()
                return

        # --- GESTION DES MESSAGES NOTE ON (Launch Control XL Factory Buttons) ---
        elif msg_type == 0x90 and data2 > 0:
            note_num = data1

            # A. Pads appris via MIDI Learn interactif (button_items ou button_types)
            btn_items = cfg.get('button_items', [])
            if btn_items:
                for item in btn_items:
                    if item.get('type') == 'note' and item.get('num') == note_num:
                        it_ch = item.get('channel')
                        if it_ch and it_ch > 0 and (channel + 1) != it_ch:
                            continue
                        target_idx = item.get('index', 0)
                        self._select_track_in_bank(target_idx)
                        return

            btn_types = cfg.get('button_types', [])
            if btn_types and len(btn_types) == NUM_TRACKS_PER_BANK:
                for idx, b_num in enumerate(cfg_buttons[:NUM_TRACKS_PER_BANK]):
                    if btn_types[idx] == 'note' and note_num == b_num:
                        self._select_track_in_bank(idx)
                        return

            # B. Launch Control XL Factory Notes (Notes 41..48 et 57..64)
            if note_num in FACTORY_BUTTON_NOTES:
                btn_idx = FACTORY_BUTTON_NOTES.index(note_num)
                if btn_idx < NUM_TRACKS_PER_BANK:
                    self._select_track_in_bank(btn_idx)
                    return
            # C. Configuration personnalisée Note
            if btn_type == 'note' and note_num in cfg_buttons:
                btn_idx = cfg_buttons.index(note_num)
                if btn_idx < NUM_TRACKS_PER_BANK:
                    self._select_track_in_bank(btn_idx)
                    return
            # D. Notes Drum Rack standard (Notes 36..51 pour boutons 1..16)
            if 36 <= note_num <= 51:
                self._select_track_in_bank(note_num - 36)
                return

        # --- GESTION DU RELÂCHEMENT DES NOTES (Note Off 0x80 ou Note On vel 0) ---
        elif msg_type == 0x80 or (msg_type == 0x90 and data2 == 0):
            note_num = data1
            btn_items = cfg.get('button_items', [])
            btn_types = cfg.get('button_types', [])
            is_button_note = (note_num in FACTORY_BUTTON_NOTES) or \
                             (btn_type == 'note' and note_num in cfg_buttons) or \
                             any(it.get('num') == note_num and it.get('type') == 'note' for it in btn_items) or \
                             (btn_types and any(btn_types[idx] == 'note' and cfg_buttons[idx] == note_num for idx in range(min(len(btn_types), len(cfg_buttons))))) or \
                             (36 <= note_num <= 51)
            if is_button_note:
                self._update_pad_leds()
                return

        super(LivePilot16, self).receive_midi(midi_bytes)

    def handle_sysex(self, midi_bytes):
        """Interception des trames SysEx Novation (changement de template / mode)"""
        if not midi_bytes:
            return
        if not self._is_master and LivePilot16._master_instance:
            LivePilot16._master_instance.handle_sysex(midi_bytes)
            return

        if len(midi_bytes) >= 6 and midi_bytes[1:4] == (0x00, 0x20, 0x29):
            mode_byte = midi_bytes[-2] if midi_bytes[-1] == 0xF7 else midi_bytes[-1]
            if mode_byte in NOVATION_MODE_TO_TRACK:
                target_trk = NOVATION_MODE_TO_TRACK[mode_byte]
                self.log_message("LivePilot : SysEx Novation Mode recu (%d) -> Selection Piste %d" % (mode_byte, target_trk + 1))
                self._select_track_in_bank(target_trk)
                return
            elif 0 <= mode_byte < NUM_TRACKS_PER_BANK:
                self._select_track_in_bank(mode_byte)
                return
        super(LivePilot16, self).handle_sysex(midi_bytes)

    def _enforce_daw_control_mode(self):
        """Force le Launch Control XL 3 en mode DAW Control (02h) avec encodeurs absolus (0..127).
        Cela garantit que Page ▲/▼ (CC 106/107) et Track ◄/► (CC 103/102) sont 100% actifs matériellement,
        ainsi que les 16 Pads, les 24 Knobs, les 8 Faders et toutes les LEDs RGB."""
        try:
            self._lcxl3_surface_mode = 'daw'
            self._send_midi_all(NOVATION_DAW_MODE_ON_SYSEX)
            self._send_midi_all(NOVATION_DAW_MODE_ON_NOTE)
            self._send_midi_all(NOVATION_FEATURE_CONTROLS_ON_NOTE)
            # Bascule explicite de la surface en mode DAW Control (Canal 7, CC 30, valeur 2)
            self._send_midi_all(NOVATION_SURFACE_DAW_CONTROL)
            # Désactivation du mode relatif sur les 3 rangées d'encodeurs (mode absolu 0..127)
            self._send_midi_all(NOVATION_ENCODER_ROW1_ABS)
            self._send_midi_all(NOVATION_ENCODER_ROW2_ABS)
            self._send_midi_all(NOVATION_ENCODER_ROW3_ABS)
        except Exception:
            pass

    def _full_resync(self):
        # Activation native du DAW Mode Novation Launch Control XL 3 (Page 8, 10 & 16 du Guide Officiel)
        # pour déverrouiller Track ◄/►, Page ▲/▼, les LEDs RGB des 24 knobs et des 16 pads, et l'écran OLED
        self._pad_led_cache = [None] * NUM_TRACKS_PER_BANK
        self._knob_led_cache = [None] * NUM_ENCODERS
        self._enforce_daw_control_mode()

        self._send_bank_info()
        self._send_bank_colors()
        self._send_scene_info()
        self._on_selected_track_changed()
        self._update_pad_leds(force=True)
        self._update_knob_leds(force=True)
        self._update_nav_leds()
        self._broadcast_full_sync()
        try:
            self.request_rebuild_midi_map()
        except Exception:
            pass

    def _schedule_led_refresh(self):
        """Rafraîchit l'état matériel uniquement pour les éléments modifiés (via cache delta)"""
        try:
            self.schedule_message(1, self._refresh_all_hardware_feedback)
        except Exception:
            pass

    def _refresh_all_hardware_feedback(self):
        self._update_pad_leds()
        self._update_knob_leds()
        self._update_nav_leds()
        self._sync_hardware_encoders()

    def _send_midi_all(self, midi_bytes):
        """Diffuse un message MIDI vers toutes les instances LivePilot16 actives (Port 1 et Port 2)"""
        for inst in list(LivePilot16._instances):
            try:
                inst._send_midi(midi_bytes)
            except Exception:
                pass

    def _send_midi_daw(self, midi_bytes):
        """Envoie un message MIDI uniquement sur le port DAW (Port 2 si présent, sinon Port 1).
        Sur Windows (Guide Programmeur LCXL3 Page 5), le Port 1 (LCXL3 1 MIDI) est l'interface Custom Modes
        où les CC 33..48 sur Canal 1 (0xB0) correspondent aux 16 boutons Custom (valeur > 0 = Rouge).
        En n'envoyant les CC de palette DAW (0xB0) que sur le Port 2 (DAW In/Out), on élimine 100% du
        conflit Rouge/Vert qui faisait clignoter les autres pads !"""
        instances = list(LivePilot16._instances)
        targets = instances[1:] if len(instances) > 1 else instances
        for inst in targets:
            try:
                inst._send_midi(midi_bytes)
            except Exception:
                pass

    def _update_pad_leds(self, force=False, force_pad_idx=None):
        """Met a jour l'etat lumineux des 16 pads physiques du Launch Control XL 3 (indices 37..52 en mode DAW).
        - Piste active selectionnee : Rouge permanent (SysEx RGB 127,0,0 + Palette 5 sur port DAW).
        - Pistes existantes non selectionnees : Vert permanent (SysEx RGB 0,127,0 + Palette 60 sur port DAW).
        - Pistes inexistantes dans le projet Ableton : Eteint / Off (SysEx RGB 0,0,0 + Palette 0 sur port DAW).
        Utilise un cache d'etat par pad (_pad_led_cache) pour n'envoyer de messages MIDI QU'AUX pads
        dont l'etat change reellement (ex: ancienne piste Rouge -> Vert, nouvelle piste Vert -> Rouge).
        Les autres pads ne recoivent aucun message MIDI lors d'une bascule et restent parfaitement stables !
        """
        try:
            if not hasattr(self, '_pad_led_cache') or len(self._pad_led_cache) != NUM_TRACKS_PER_BANK:
                self._pad_led_cache = [None] * NUM_TRACKS_PER_BANK

            selected_track = self.song().view.selected_track
            tracks = list(self.song().tracks)
            total_tracks = len(tracks)
            start_idx = self._current_bank_index * NUM_TRACKS_PER_BANK
            active_pad_idx = -1
            if selected_track in tracks:
                track_idx = tracks.index(selected_track)
                if start_idx <= track_idx < start_idx + NUM_TRACKS_PER_BANK:
                    active_pad_idx = track_idx - start_idx

            for i in range(NUM_TRACKS_PER_BANK):
                global_trk_idx = start_idx + i
                track_exists = (global_trk_idx < total_tracks)
                if track_exists:
                    desired_state = 'red' if (i == active_pad_idx) else 'green'
                else:
                    desired_state = 'off'

                if not force and force_pad_idx != i and self._pad_led_cache[i] == desired_state:
                    continue

                self._pad_led_cache[i] = desired_state
                ctrl_idx = LCXL3_BUTTON_INDICES[i] if (i < len(LCXL3_BUTTON_INDICES)) else (37 + i)

                if desired_state == 'red':
                    # Piste sélectionnée -> ROUGE PERMANENT (SysEx RGB 127,0,0 + Palette 5 sur port DAW)
                    self._send_midi_all((0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x01, 0x53, ctrl_idx, 127, 0, 0, 0xF7))
                    self._send_midi_daw((0xB0, ctrl_idx, 5))
                elif desired_state == 'green':
                    # Piste existante non sélectionnée -> VERT PERMANENT (SysEx RGB 0,127,0 + Palette 60 sur port DAW)
                    self._send_midi_all((0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x01, 0x53, ctrl_idx, 0, 127, 0, 0xF7))
                    self._send_midi_daw((0xB0, ctrl_idx, 60))
                else:
                    # Piste inexistante -> ÉTEINT (SysEx RGB 0,0,0 + Palette 0 sur port DAW)
                    self._send_midi_all((0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x01, 0x53, ctrl_idx, 0, 0, 0, 0xF7))
                    self._send_midi_daw((0xB0, ctrl_idx, 0))
        except Exception as e:
            self.log_message("LivePilot : Erreur dans _update_pad_leds : %s" % str(e))

    def _update_knob_leds(self, force=False):
        """Met a jour les LEDs sous les 24 potentiometres du Launch Control XL 3 (indices 13..36 en mode DAW).
        - Si le plugin actif possede un parametre pour ce knob : allume la LED de sa rangee.
        - Si aucun plugin ou parametre inexistant : eteint la LED (SysEx RGB 0,0,0 + Palette 0 sur port DAW).
        Utilise un cache (_knob_led_cache) et n'envoie jamais de CC 0xB0 sur le Port 1 Custom Mode
        (ou les CC 33..36 correspondent aux Pads 1..4).
        """
        try:
            if not hasattr(self, '_knob_led_cache') or len(self._knob_led_cache) != NUM_ENCODERS:
                self._knob_led_cache = [None] * NUM_ENCODERS

            dev = self._current_device
            num_params = len(dev.parameters[1:]) if dev else 0

            # Couleurs distinctes pour les 3 rangées de potentiomètres (Palette Novation DAW + RGB) :
            # Ligne 1 (Knobs 1..8,  indices 13..20) : Cyan (Palette 37, RGB 0,127,127)
            # Ligne 2 (Knobs 9..16, indices 21..28) : Ambre / Jaune (Palette 13, RGB 127,80,0)
            # Ligne 3 (Knobs 17..24, indices 29..36) : Magenta / Violet (Palette 53, RGB 127,0,127)
            row_colors = [
                (0, 127, 127, 37),
                (127, 80, 0, 13),
                (127, 0, 127, 53)
            ]

            for k in range(NUM_ENCODERS):
                is_active = bool(dev and k < num_params)
                if not force and self._knob_led_cache[k] == is_active:
                    continue
                self._knob_led_cache[k] = is_active

                ctrl_idx = 13 + k
                row = k // 8
                r, g, b, pal_cc = row_colors[min(row, 2)]

                if is_active:
                    self._send_midi_all((0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x01, 0x53, ctrl_idx, r, g, b, 0xF7))
                    self._send_midi_daw((0xB0, ctrl_idx, pal_cc))
                else:
                    self._send_midi_all((0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x01, 0x53, ctrl_idx, 0, 0, 0, 0xF7))
                    self._send_midi_daw((0xB0, ctrl_idx, 0))
        except Exception as e:
            self.log_message("LivePilot : Erreur dans _update_knob_leds : %s" % str(e))

    def _is_nav_action_available(self, action):
        """Retourne True si l'action de navigation assignée est disponible dans le contexte actuel"""
        if not action or action == 'none':
            return False
        if action == 'device_prev':
            return len(self._assigned_devices) > 1 and self._current_device_idx > 0
        if action == 'device_next':
            return len(self._assigned_devices) > 1 and self._current_device_idx < len(self._assigned_devices) - 1
        if action == 'bank_prev':
            return self._current_bank_index > 0
        if action == 'bank_next':
            total_tracks = len(self.song().tracks)
            total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
            return self._current_bank_index < total_banks - 1
        if action == 'track_prev':
            tracks = list(self.song().tracks)
            sel = self.song().view.selected_track
            return (sel in tracks) and (tracks.index(sel) > 0)
        if action == 'track_next':
            tracks = list(self.song().tracks)
            sel = self.song().view.selected_track
            return (sel in tracks) and (tracks.index(sel) < len(tracks) - 1)
        return True

    def _update_nav_leds(self):
        """Met a jour les LEDs des touches matérielles (Track ◄/►, Page ▲/▼, Play, Record)"""
        try:
            cfg = getattr(self, '_midi_config', {})
            nav_cfg = cfg.get('nav_buttons', DEFAULT_NAV_BUTTONS) if isinstance(cfg, dict) else DEFAULT_NAV_BUTTONS

            tl_act = nav_cfg.get('track_left', {}).get('action', 'device_prev') if isinstance(nav_cfg, dict) else 'device_prev'
            tr_act = nav_cfg.get('track_right', {}).get('action', 'device_next') if isinstance(nav_cfg, dict) else 'device_next'
            pu_act = nav_cfg.get('page_up', {}).get('action', 'bank_prev') if isinstance(nav_cfg, dict) else 'bank_prev'
            pd_act = nav_cfg.get('page_down', {}).get('action', 'bank_next') if isinstance(nav_cfg, dict) else 'bank_next'

            # Touches Track ◄ (103) et Track ► (102) : Allumées (Blanc/Vert vif 60) si le plugin -1 / +1 existe, éteintes (0) sinon
            tl_col = 60 if self._is_nav_action_available(tl_act) else 0
            tr_col = 60 if self._is_nav_action_available(tr_act) else 0
            self._send_midi_daw((0xB0, CC_NAV_TRACK_LEFT, tl_col))
            self._send_midi_daw((0xB0, CC_NAV_TRACK_RIGHT, tr_col))

            # Touches Page ▲ (106) et Page ▼ (107) : Allumées (Cyan vif 37) si la banque existe, éteintes (0) sinon
            pu_col = 37 if self._is_nav_action_available(pu_act) else 0
            pd_col = 37 if self._is_nav_action_available(pd_act) else 0
            self._send_midi_daw((0xB0, CC_NAV_PAGE_UP, pu_col))
            self._send_midi_daw((0xB0, CC_NAV_PAGE_DOWN, pd_col))

            # Touche Play (116) : Vert vif (60) si en lecture, éteint (0) à l'arrêt
            is_playing = self.song().is_playing
            self._send_midi_daw((0xB0, CC_HW_PLAY, 60 if is_playing else 0))

            # Touche Record (118) : Rouge vif (5) si enregistrement actif, éteint (0) sinon
            is_recording = self.song().record_mode
            self._send_midi_daw((0xB0, CC_HW_RECORD, 5 if is_recording else 0))
        except Exception as e:
            self.log_message("LivePilot : Erreur dans _update_nav_leds : %s" % str(e))

    def _update_screen_display(self):
        """Affiche le nom de la piste active et du device sur l'écran OLED du Launch Control XL 3"""
        try:
            if not self._current_track:
                return
            t_name = self._current_track.name
            clean_track = ''.join([c for c in t_name if 32 <= ord(c) <= 126])[:16]
            if not clean_track:
                clean_track = "Piste"

            d_name = self._current_device.name if self._current_device else "Cockpit Mode"
            clean_dev = ''.join([c for c in d_name if 32 <= ord(c) <= 126])[:16]

            # Configuration affichage stationnaire (Target 0x35, arrangement 1: 2 lignes)
            self._send_midi_all((0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x04, 0x35, 0x01, 0xF7))

            # Ligne 1 : Nom de la piste (Field 0)
            tb1 = [ord(c) for c in clean_track]
            self._send_midi_all(tuple([0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x06, 0x35, 0x00] + tb1 + [0xF7]))

            # Ligne 2 : Nom du plugin (Field 1)
            tb2 = [ord(c) for c in clean_dev]
            self._send_midi_all(tuple([0xF0, 0x00, 0x20, 0x29, 0x02, 0x15, 0x06, 0x35, 0x01] + tb2 + [0xF7]))
        except Exception as e:
            self.log_message("LivePilot : Erreur dans _update_screen_display : %s" % str(e))

    def _send_bank_info(self):
        total_tracks = len(self.song().tracks)
        total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
        sysex_msg = list(SYSEX_HEADER) + [CMD_BANK_INFO, self._current_bank_index, total_banks, total_tracks, 0xF7]
        self._send_midi(tuple(sysex_msg))
        self._update_pad_leds()

    def _send_bank_colors(self):
        colors_payload = []
        tracks = self.song().tracks
        start_idx = self._current_bank_index * NUM_TRACKS_PER_BANK
        for i in range(NUM_TRACKS_PER_BANK):
            track_idx = start_idx + i
            if track_idx < len(tracks):
                track = tracks[track_idx]
                is_selected = (track == self._current_track)
                has_assignments = self._track_has_assignments(track)
                if is_selected and not has_assignments:
                    colors_payload.extend([127, 127, 127])
                else:
                    color_int = track.color
                    r = ((color_int >> 16) & 0xFF) >> 1
                    g = ((color_int >> 8) & 0xFF) >> 1
                    b = (color_int & 0xFF) >> 1
                    colors_payload.extend([r, g, b])
            else:
                colors_payload.extend([0, 0, 0])
        sysex_msg = list(SYSEX_HEADER) + [CMD_BANK_COLORS] + colors_payload + [0xF7]
        self._send_midi(tuple(sysex_msg))

    def _send_active_track_info(self):
        if not self._current_track:
            return
        is_group = 1 if getattr(self._current_track, 'is_foldable', False) else 0
        has_assign_flag = 1 if self._track_has_assignments(self._current_track) else 0
        prefix = "[GRP] " if is_group else ""
        track_name = (prefix + self._current_track.name)[:16]
        name_bytes = [ord(c) & 0x7F for c in track_name]
        try:
            track_index = list(self.song().tracks).index(self._current_track)
        except ValueError:
            track_index = 0
        sysex_msg = list(SYSEX_HEADER) + [CMD_TRACK_ACTIVE, track_index, has_assign_flag, is_group] + name_bytes + [0x00, 0xF7]
        self._send_midi(tuple(sysex_msg))

    def _send_active_device_info(self):
        total_assigned = len(self._assigned_devices)
        nav_enabled = 1 if total_assigned > 1 else 0
        if total_assigned == 0 or not self._current_device:
            dev_name = "No Assignment"
            dev_idx = 0
        else:
            dev_name = self._current_device.name[:28]
            dev_idx = self._current_device_idx
        name_bytes = [ord(c) & 0x7F for c in dev_name]
        sysex_msg = list(SYSEX_HEADER) + [CMD_DEVICE_ACTIVE, dev_idx, total_assigned, nav_enabled] + name_bytes + [0x00, 0xF7]
        self._send_midi(tuple(sysex_msg))

    def _send_parameters_info(self):
        if not self._current_device:
            for idx in range(NUM_ENCODERS):
                payload = [CMD_PARAM_DATA, idx, 0, ord('-'), 0x00, 0x00, 0xF7]
                self._send_midi(tuple(list(SYSEX_HEADER) + payload))
            return
        params = self._current_device.parameters[1:NUM_ENCODERS+1]
        for idx in range(NUM_ENCODERS):
            if idx < len(params):
                param = params[idx]
                p_name = param.name[:12]
                p_val_str = str(param)[:8]
                val_range = max(0.0001, (param.max - param.min))
                val_7bit = int((param.value - param.min) / val_range * 127)
                name_bytes = [ord(c) & 0x7F for c in p_name]
                val_str_bytes = [ord(c) & 0x7F for c in p_val_str]
                payload = [CMD_PARAM_DATA, idx, val_7bit] + name_bytes + [0x00] + val_str_bytes + [0x00, 0xF7]
            else:
                payload = [CMD_PARAM_DATA, idx, 0, ord('-'), 0x00, 0x00, 0xF7]
            self._send_midi(tuple(list(SYSEX_HEADER) + payload))

    def _send_scene_info(self):
        song = self.song()
        playing_scene = None
        playing_idx = 0
        for idx, sc in enumerate(song.scenes):
            if getattr(sc, 'is_playing', False):
                playing_scene = sc
                playing_idx = idx
                break
        is_playing = 1 if (playing_scene is not None and song.is_playing) else 0
        if not playing_scene:
            playing_scene = song.view.selected_scene
            try:
                playing_idx = list(song.scenes).index(playing_scene)
            except Exception:
                playing_idx = 0

        color_int = getattr(playing_scene, 'color', 0) if playing_scene else 0
        r = ((color_int >> 16) & 0xFF) >> 1
        g = ((color_int >> 8) & 0xFF) >> 1
        b = (color_int & 0xFF) >> 1

        tempo = float(song.tempo)
        bpm_int = int(tempo)
        bpm_high = (bpm_int >> 7) & 0x7F
        bpm_low = bpm_int & 0x7F
        bpm_dec = int((tempo - bpm_int) * 10) & 0x7F

        raw_name = playing_scene.name if (playing_scene and playing_scene.name) else ("Scene %d" % (playing_idx + 1))
        sc_name = raw_name[:96]
        name_bytes = [ord(c) & 0x7F for c in sc_name]
        sysex_msg = list(SYSEX_HEADER) + [CMD_SCENE_INFO, playing_idx & 0x7F, is_playing, bpm_high, bpm_low, bpm_dec, r, g, b] + name_bytes + [0x00, 0xF7]
        self._send_midi(tuple(sysex_msg))

    def _adjust_master_jog(self, delta):
        if getattr(self, '_master_mode_bpm', True):
            new_tempo = max(20.0, min(999.0, self.song().tempo + delta))
            self.song().tempo = new_tempo
            self._send_scene_info()
            self._broadcast_transport()
        else:
            scenes = list(self.song().scenes)
            if scenes:
                try:
                    cur_idx = scenes.index(self.song().view.selected_scene)
                except ValueError:
                    cur_idx = 0
                new_idx = max(0, min(len(scenes) - 1, cur_idx + delta))
                self.song().view.selected_scene = scenes[new_idx]
                self._send_scene_info()
                self._broadcast_active_scene()

    def _toggle_master_mode(self):
        self._master_mode_bpm = not getattr(self, '_master_mode_bpm', True)

    def _nav_screen_left(self):
        scenes = list(self.song().scenes)
        if scenes:
            try:
                cur_idx = scenes.index(self.song().view.selected_scene)
            except ValueError:
                cur_idx = 0
            if cur_idx > 0:
                self.song().view.selected_scene = scenes[cur_idx - 1]
                self._send_scene_info()
                self._broadcast_active_scene()

    def _nav_screen_right(self):
        scenes = list(self.song().scenes)
        if scenes:
            try:
                cur_idx = scenes.index(self.song().view.selected_scene)
            except ValueError:
                cur_idx = 0
            if cur_idx < len(scenes) - 1:
                self.song().view.selected_scene = scenes[cur_idx + 1]
                self._send_scene_info()
                self._broadcast_active_scene()

    def _on_btn_valid_pressed(self):
        if self.song().view.selected_scene:
            self.song().view.selected_scene.fire()
            self._send_scene_info()
            self._broadcast_active_scene()
