# -*- coding: utf-8 -*-
# LivePilot 16 — Module Principal du Remote Script Ableton Live
# Architecture Live Cockpit : Launch Control XL + Launchpad Pro MK3 + Tablette Android (HUD)
# "Ne regardez plus l'écran, pilotez votre son."

from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.ControlSurface import ControlSurface
from .consts import (
    SYSEX_HEADER, CMD_BANK_INFO, CMD_TRACK_ACTIVE, CMD_BANK_COLORS,
    CMD_DEVICE_ACTIVE, CMD_PARAM_DATA, CMD_SCENE_INFO, CC_BASE_ENCODERS,
    CC_ENC17_JOG, CC_ENC17_PUSH, CC_NAV_LEFT, CC_NAV_RIGHT, CC_BTN_VALID,
    CC_NAV_TRACK_PREV, CC_NAV_TRACK_NEXT, CC_NAV_GROUP_PREV, CC_NAV_GROUP_NEXT,
    CC_NAV_DEV_PREV, CC_NAV_DEV_NEXT, CC_BASE_TRACK_SEL,
    NUM_TRACKS_PER_BANK, NUM_ENCODERS, DEFAULT_HTTP_PORT
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
    """
    Surface de contrôle officielle LivePilot pour Ableton Live.
    
    Gestion intégrée du Setup Live sans écran d'ordinateur :
    - Launchpad Pro MK3 : Lancement de clips / scènes, session, note mode.
    - Launch Control XL : 8 faders de volume, 24 knobs pour les plugins et envois.
    - Tablette Android (Cockpit Web) : Affichage tête haute (HUD) temps réel via WebSocket.
    """

    def __init__(self, c_instance):
        super(LivePilot16, self).__init__(c_instance)
        self.log_message("LivePilot : Initialisation du Remote Script & Serveur Cockpit...")

        self._current_bank_index = 0
        self._current_track = None
        self._assigned_devices = []
        self._current_device_idx = 0
        self._current_device = None
        self._observed_params = []
        self._observed_scenes = []
        self._master_mode_bpm = True
        self._meter_polling_active = False

        # Démarrage du serveur Web / WebSocket pour la tablette Android
        self._web_server = LivePilotWebServer(
            port=DEFAULT_HTTP_PORT,
            on_client_message=self._on_web_client_message,
            logger=self.log_message
        )
        self._web_server.start()

        # Initialisation des écouteurs LOM
        with self.component_guard():
            self._setup_listeners()
            self._full_resync()

        # Démarrage de la boucle de polling des VU-mètres
        self._schedule_meter_poll()

        self.log_message("LivePilot : Pret pour le Live !")

    def disconnect(self):
        """Nettoyage lors de la fermeture d'Ableton Live"""
        self.log_message("LivePilot : Deconnexion de la surface de controle.")
        if self._web_server:
            self._web_server.stop()
            self._web_server = None
        self._cleanup_listeners()
        self._detach_scene_listeners()
        self._remove_parameter_listeners()
        super(LivePilot16, self).disconnect()

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

    def _on_scene_selection_changed(self):
        self._send_scene_info()
        self._broadcast_active_scene()

    def _on_scene_status_changed(self):
        self._send_scene_info()
        self._broadcast_active_scene()

    def _on_tracks_changed(self):
        self._send_bank_info()
        self._send_bank_colors()
        self._broadcast_full_sync()

    def _on_selected_track_changed(self):
        self._current_track = self.song().view.selected_track
        # Aligne automatiquement la banque si la piste sélectionnée est hors de la banque courante
        self._auto_align_bank_for_track(self._current_track)
        self._refresh_assigned_devices()
        self._send_active_track_info()
        self._send_bank_colors()
        self._send_active_device_info()
        self._send_parameters_info()
        self._broadcast_selected_track()

    def _auto_align_bank_for_track(self, track):
        """Ajuste automatiquement la banque visible de 8 pistes si nécessaire"""
        tracks = list(self.song().tracks)
        if track in tracks:
            idx = tracks.index(track)
            target_bank = idx // NUM_TRACKS_PER_BANK
            if target_bank != self._current_bank_index:
                self._current_bank_index = target_bank
                self._send_bank_info()
                self._send_bank_colors()

    # =========================================================================
    # GESTION DES DEVICES & PARAMÈTRES
    # =========================================================================
    def _device_has_assignments(self, device):
        if not device:
            return False
        return len(device.parameters) > 1

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
        if not self._can_navigate_devices():
            return
        self._current_device_idx = (self._current_device_idx - 1) % len(self._assigned_devices)
        self._current_device = self._assigned_devices[self._current_device_idx]
        self._attach_parameter_listeners()
        self._send_active_device_info()
        self._send_parameters_info()
        self._broadcast_selected_device()

    def _nav_device_next(self):
        if not self._can_navigate_devices():
            return
        self._current_device_idx = (self._current_device_idx + 1) % len(self._assigned_devices)
        self._current_device = self._assigned_devices[self._current_device_idx]
        self._attach_parameter_listeners()
        self._send_active_device_info()
        self._send_parameters_info()
        self._broadcast_selected_device()

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

    def _adjust_parameter(self, encoder_idx, rel_value):
        if not self._current_device or encoder_idx >= NUM_ENCODERS:
            return
        params = self._current_device.parameters[1:NUM_ENCODERS+1]
        if encoder_idx < len(params):
            p = params[encoder_idx]
            step = (p.max - p.min) / 127.0
            new_val = p.value + (rel_value * step)
            p.value = max(p.min, min(p.max, new_val))

    # =========================================================================
    # NAVIGATION DE BANQUES & PISTES
    # =========================================================================
    def _nav_bank_prev(self):
        if self._current_bank_index > 0:
            self._current_bank_index -= 1
            self._send_bank_info()
            self._send_bank_colors()
            self._broadcast_full_sync()

    def _nav_bank_next(self):
        total_tracks = len(self.song().tracks)
        total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
        if self._current_bank_index < total_banks - 1:
            self._current_bank_index += 1
            self._send_bank_info()
            self._send_bank_colors()
            self._broadcast_full_sync()

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
                self._send_bank_info()
                self._send_bank_colors()
            self.song().view.selected_track = target_track

    def _select_track_in_bank(self, index_in_bank):
        track_idx = (self._current_bank_index * NUM_TRACKS_PER_BANK) + index_in_bank
        tracks = self.song().tracks
        if 0 <= track_idx < len(tracks):
            target_track = tracks[track_idx]
            if target_track == self.song().view.selected_track and getattr(target_track, 'is_foldable', False):
                try:
                    target_track.fold_state = not target_track.fold_state
                except Exception:
                    pass
            else:
                self.song().view.selected_track = target_track

    # =========================================================================
    # DIFFUSION WEBSOCKET (Ableton -> Tablette Android)
    # =========================================================================
    def _build_track_dict(self, track, global_index):
        if not track:
            return None
        vol_str = str(track.mixer_device.volume) if hasattr(track, 'mixer_device') else '0 dB'
        pan_str = str(track.mixer_device.panning) if hasattr(track, 'mixer_device') else 'C'
        is_group = bool(getattr(track, 'is_foldable', False))
        fold_state = bool(getattr(track, 'fold_state', False)) if is_group else False
        is_grouped = bool(getattr(track, 'is_grouped', False))
        group_name = track.group_track.name if (is_grouped and getattr(track, 'group_track', None)) else ""

        return {
            'index': global_index,
            'name': track.name,
            'color': int_to_hex_color(getattr(track, 'color', None)),
            'is_group': is_group,
            'fold_state': fold_state,
            'is_grouped': is_grouped,
            'group_name': group_name,
            'mute': bool(getattr(track, 'mute', False)),
            'solo': bool(getattr(track, 'solo', False)),
            'arm': bool(getattr(track, 'arm', False)),
            'vol_str': vol_str,
            'pan_str': pan_str
        }

    def _build_params_list(self):
        params_out = []
        if not self._current_device:
            for i in range(NUM_ENCODERS):
                params_out.append({'index': i, 'name': '-', 'value': 0.0, 'str': '-'})
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
                    'str': str(p)[:10]
                })
            else:
                params_out.append({'index': i, 'name': '-', 'value': 0.0, 'str': '-'})
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
        
        # Ligne 2 : Descriptif / annotations scéniques complètes
        desc_line = "Scène %d / %d  •  Tempo: %.1f BPM  •  Signature: %d/%d  •  Session Live" % (
            scene_idx + 1, total_sc, tempo, sig_num, sig_den
        )

        return {
            'num': scene_idx + 1,
            'total': total_sc,
            'name': sc_name,
            'desc': desc_line,
            'color': int_to_hex_color(getattr(active_sc, 'color', None)) if active_sc else '#1e2230',
            'is_playing': bool(song.is_playing)
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
        song = self.song()
        tracks = song.tracks
        total_tracks = len(tracks)
        total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)

        # 16 pistes de la banque courante (miroir des 16 boutons du Launch Control XL)
        bank_tracks = []
        start_idx = self._current_bank_index * NUM_TRACKS_PER_BANK
        for i in range(NUM_TRACKS_PER_BANK):
            t_idx = start_idx + i
            if t_idx < total_tracks:
                bank_tracks.append(self._build_track_dict(tracks[t_idx], t_idx))
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
            'parameters': self._build_params_list()
        }
        self._web_server.broadcast({'type': 'full_sync', 'data': payload})

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
        tracks = list(self.song().tracks)
        try:
            sel_idx = tracks.index(self._current_track) if self._current_track in tracks else 0
        except ValueError:
            sel_idx = 0

        bank_tracks = []
        start_idx = self._current_bank_index * NUM_TRACKS_PER_BANK
        for i in range(NUM_TRACKS_PER_BANK):
            t_idx = start_idx + i
            if t_idx < len(tracks):
                bank_tracks.append(self._build_track_dict(tracks[t_idx], t_idx))
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
                'label': "[%d/%d] %s" % (idx + 1, total_devs, dev.name)
            })

        active_dev_label = "[%d/%d] %s" % (self._current_device_idx + 1, total_devs, self._current_device.name) if self._current_device else "No Assignment"

        self._web_server.broadcast({
            'type': 'track_selected',
            'data': {
                'track_index': sel_idx,
                'tracks': bank_tracks,
                'devices': devs_data,
                'active_device_name': active_dev_label,
                'active_device_index': self._current_device_idx,
                'parameters': self._build_params_list()
            }
        })

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

        elif action == 'select_track':
            t_idx = msg.get('track_index', 0)
            tracks = list(self.song().tracks)
            if 0 <= t_idx < len(tracks):
                self.song().view.selected_track = tracks[t_idx]

        elif action == 'select_device':
            d_idx = msg.get('device_index', 0)
            if 0 <= d_idx < len(self._assigned_devices):
                self._current_device_idx = d_idx
                self._current_device = self._assigned_devices[d_idx]
                self._attach_parameter_listeners()
                self._send_active_device_info()
                self._send_parameters_info()
                self._broadcast_selected_device()

        elif action == 'set_parameter':
            p_idx = msg.get('index', 0)
            norm_val = msg.get('value', 0.0)
            if self._current_device:
                params = self._current_device.parameters[1:NUM_ENCODERS+1]
                if 0 <= p_idx < len(params):
                    p = params[p_idx]
                    p.value = p.min + norm_val * (p.max - p.min)

        elif action == 'trigger_scene':
            sc_idx = msg.get('scene_index', 0)
            scenes = list(self.song().scenes)
            if 0 <= sc_idx < len(scenes):
                scenes[sc_idx].fire()

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

        elif action == 'select_bank':
            b_idx = int(msg.get('bank_index', 0))
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

        elif action in ('toggle_mute', 'toggle_solo', 'toggle_arm'):
            t_idx = msg.get('track_index', 0)
            tracks = list(self.song().tracks)
            if 0 <= t_idx < len(tracks):
                t = tracks[t_idx]
                if action == 'toggle_mute':
                    t.mute = not t.mute
                elif action == 'toggle_solo':
                    t.solo = not t.solo
                elif action == 'toggle_arm':
                    t.arm = not t.arm
                self._broadcast_selected_track()

    # =========================================================================
    # COMPATIBILITÉ MIDI / SYSEX (Matériel physique optionnel)
    # =========================================================================
    def receive_midi(self, midi_bytes):
        if len(midi_bytes) < 3:
            return
        status, data1, data2 = midi_bytes[0], midi_bytes[1], midi_bytes[2]
        if (status & 0xF0) == 0xB0:
            cc_num, cc_val = data1, data2
            if CC_BASE_TRACK_SEL <= cc_num < CC_BASE_TRACK_SEL + NUM_TRACKS_PER_BANK:
                if cc_val > 0:
                    self._select_track_in_bank(cc_num - CC_BASE_TRACK_SEL)
                    return
            elif cc_num == CC_NAV_TRACK_PREV and cc_val > 0:
                self._nav_bank_prev()
                return
            elif cc_num == CC_NAV_TRACK_NEXT and cc_val > 0:
                self._nav_bank_next()
                return
            elif cc_num == CC_NAV_GROUP_PREV and cc_val > 0:
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
            elif CC_BASE_ENCODERS <= cc_num < CC_BASE_ENCODERS + NUM_ENCODERS:
                delta = cc_val if cc_val < 64 else (cc_val - 128)
                self._adjust_parameter(cc_num - CC_BASE_ENCODERS, delta)
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
        super(LivePilot16, self).receive_midi(midi_bytes)

    def _full_resync(self):
        self._send_bank_info()
        self._send_bank_colors()
        self._send_scene_info()
        self._on_selected_track_changed()
        self._broadcast_full_sync()

    def _send_bank_info(self):
        total_tracks = len(self.song().tracks)
        total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
        sysex_msg = list(SYSEX_HEADER) + [CMD_BANK_INFO, self._current_bank_index, total_banks, total_tracks, 0xF7]
        self._send_midi(tuple(sysex_msg))

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
