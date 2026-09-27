# LivePilot 16 — Module Principal du Remote Script Ableton Live
# Slogan : "Ne regardez plus l'écran, pilotez votre son."

from __future__ import absolute_import, print_function, unicode_literals
import Live
from _Framework.ControlSurface import ControlSurface
from .consts import (
    SYSEX_HEADER, CMD_BANK_INFO, CMD_TRACK_ACTIVE, CMD_BANK_COLORS,
    CMD_DEVICE_ACTIVE, CMD_PARAM_DATA, CMD_SCENE_INFO, CC_BASE_ENCODERS,
    CC_ENC17_JOG, CC_ENC17_PUSH, CC_NAV_LEFT, CC_NAV_RIGHT, CC_BTN_VALID,
    CC_NAV_TRACK_PREV, CC_NAV_TRACK_NEXT, CC_NAV_GROUP_PREV, CC_NAV_GROUP_NEXT,
    CC_NAV_DEV_PREV, CC_NAV_DEV_NEXT, CC_BASE_TRACK_SEL,
    NUM_TRACKS_PER_BANK, NUM_ENCODERS
)

class LivePilot16(ControlSurface):
    """
    Surface de contrôle officielle LivePilot 16 pour Ableton Live.
    
    Gestion intégrée :
    - 6 Touches de Navigation Dédiées :
      * TRACK - / TRACK +   : Saut de banque (16 pistes)
      * GROUP - / GROUP +   : Navigation macro directe de groupe en groupe / bus en bus
      * DEVICE - / DEVICE + : Navigation intelligente entre plugins assignés (condition > 1)
    - Détection des Pistes de Groupe (Group Tracks & Traitements de Bus).
    - Règle de la touche blanche : Piste sélectionnée sans assignation = BLANC PUR.
    - Bascule Pliage / Dépliage (Fold / Unfold) automatique en cas de ré-appui sur un groupe.
    - Suivi de la Scène en lecture (Couleur Ableton en fond) & Tempo en haut à droite.
    """

    def __init__(self, c_instance):
        super(LivePilot16, self).__init__(c_instance)
        self.log_message("LivePilot 16 : Initialisation du Remote Script v1.6 (Scene Banner & Tempo)...")
        
        self._current_bank_index = 0
        self._current_track = None
        self._assigned_devices = []
        self._current_device_idx = 0
        self._current_device = None
        self._observed_params = []
        self._observed_scenes = []
        
        # Initialisation des écouteurs temps réel
        with self.component_guard():
            self._setup_listeners()
            self._full_resync()
            
        self.log_message("LivePilot 16 : Initialisation terminee avec succes !")

    def disconnect(self):
        """Nettoyage lors de la fermeture d'Ableton Live"""
        self.log_message("LivePilot 16 : Deconnexion de la surface de controle.")
        self._cleanup_listeners()
        self._detach_scene_listeners()
        self._remove_parameter_listeners()
        super(LivePilot16, self).disconnect()

    def _setup_listeners(self):
        """Attache les écouteurs sur le Live Object Model (LOM)"""
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
        self._attach_scene_listeners()

    def _cleanup_listeners(self):
        """Détache proprement les écouteurs"""
        song = self.song()
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
        """Attache les écouteurs d'état et de couleur sur toutes les scènes"""
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
        """Détache proprement les écouteurs sur les scènes"""
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

    def _on_play_state_changed(self):
        self._send_scene_info()

    def _on_scenes_list_changed(self):
        self._attach_scene_listeners()
        self._send_scene_info()

    def _on_scene_selection_changed(self):
        self._send_scene_info()

    def _on_scene_status_changed(self):
        self._send_scene_info()

    def _on_tracks_changed(self):
        """Appelé lors de l'ajout, suppression ou regroupement de pistes"""
        self._send_bank_info()
        self._send_bank_colors()

    def _on_selected_track_changed(self):
        """Appelé dès que la piste sélectionnée change dans Ableton (Piste standard ou Groupe)"""
        self._current_track = self.song().view.selected_track
        self._refresh_assigned_devices()
        self._send_active_track_info()
        self._send_bank_colors()  # Rafraîchit les couleurs (blanc pur si groupe/piste non assigné)
        self._send_active_device_info()
        self._send_parameters_info()

    # =========================================================================
    # RÈGLE 1 : DÉTECTION DES ASSIGNATIONS (PISTES STANDARDS ET GROUPES)
    # =========================================================================
    def _device_has_assignments(self, device):
        """Vérifie si un device comporte des paramètres assignés / contrôlables"""
        if not device:
            return False
        # Un device est considéré comme ayant des assignations s'il a plus d'un paramètre (exclut le simple On/Off)
        # ou s'il s'agit d'un Rack avec des Macro-commandes actives
        return len(device.parameters) > 1

    def _track_has_assignments(self, track):
        """
        Retourne True si la piste (ou le groupe) possède au moins un device assigné sur son bus.
        Fonctionne de manière transparente que 'track' soit une piste audio, MIDI ou une piste Groupe.
        """
        if not track:
            return False
        for dev in track.devices:
            if self._device_has_assignments(dev):
                return True
        return False

    def _refresh_assigned_devices(self):
        """
        Filtre les devices de la piste ou du groupe actif.
        Pour un groupe, track.devices contient les effets de bus globaux (compresseur de groupe, etc.).
        """
        self._remove_parameter_listeners()
        self._assigned_devices = []
        if self._current_track:
            for dev in self._current_track.devices:
                if self._device_has_assignments(dev):
                    self._assigned_devices.append(dev)

        # Sélectionne le premier device assigné du groupe ou de la piste
        if len(self._assigned_devices) > 0:
            self._current_device_idx = 0
            self._current_device = self._assigned_devices[0]
            self._attach_parameter_listeners()
        else:
            self._current_device_idx = 0
            self._current_device = None

    # =========================================================================
    # RÈGLE 2 : PARCOURS INTELLIGENT DE DEVICES (STRICTEMENT > 1)
    # =========================================================================
    def _can_navigate_devices(self):
        """La navigation n'est autorisée que s'il y a PLUS d'un device assigné (> 1)"""
        return len(self._assigned_devices) > 1

    def _nav_device_prev(self):
        """Bascule sur le device assigné précédent sur la piste ou le groupe (si > 1)"""
        if not self._can_navigate_devices():
            return  # Verrouillé : 0 ou 1 seul plugin assigné sur le groupe/piste
        self._current_device_idx = (self._current_device_idx - 1) % len(self._assigned_devices)
        self._current_device = self._assigned_devices[self._current_device_idx]
        self._attach_parameter_listeners()
        self._send_active_device_info()
        self._send_parameters_info()

    def _nav_device_next(self):
        """Bascule sur le device assigné suivant sur la piste ou le groupe (si > 1)"""
        if not self._can_navigate_devices():
            return  # Verrouillé : 0 ou 1 seul plugin assigné sur le groupe/piste
        self._current_device_idx = (self._current_device_idx + 1) % len(self._assigned_devices)
        self._current_device = self._assigned_devices[self._current_device_idx]
        self._attach_parameter_listeners()
        self._send_active_device_info()
        self._send_parameters_info()

    # =========================================================================
    # RÈGLE 3 : NAVIGATION MACRO PAR GROUPES (GROUP - / GROUP +)
    # =========================================================================
    def _get_all_groups(self):
        """Retourne la liste ordonnée de toutes les pistes de groupe du projet"""
        return [t for t in self.song().tracks if getattr(t, 'is_foldable', False)]

    def _nav_group_prev(self):
        """Saute directement au groupe / bus précédent dans le projet"""
        groups = self._get_all_groups()
        if not groups:
            self.log_message("LivePilot 16 : Aucun groupe dans le projet.")
            return
        
        tracks = list(self.song().tracks)
        current_idx = tracks.index(self._current_track) if self._current_track in tracks else 0
        
        # Cherche le groupe situé avant la piste courante
        prev_group = None
        for g in reversed(groups):
            g_idx = tracks.index(g)
            if g_idx < current_idx:
                prev_group = g
                break
                
        # Bouclage : si on est avant le 1er groupe, on va sur le dernier
        if not prev_group:
            prev_group = groups[-1]
            
        self._select_and_ensure_bank_visible(prev_group)

    def _nav_group_next(self):
        """Saute directement au groupe / bus suivant dans le projet"""
        groups = self._get_all_groups()
        if not groups:
            self.log_message("LivePilot 16 : Aucun groupe dans le projet.")
            return
            
        tracks = list(self.song().tracks)
        current_idx = tracks.index(self._current_track) if self._current_track in tracks else -1
        
        # Cherche le groupe situé après la piste courante
        next_group = None
        for g in groups:
            g_idx = tracks.index(g)
            if g_idx > current_idx:
                next_group = g
                break
                
        # Bouclage : si on est après le dernier groupe, on revient au premier
        if not next_group:
            next_group = groups[0]
            
        self._select_and_ensure_bank_visible(next_group)

    def _select_and_ensure_bank_visible(self, target_track):
        """Sélectionne la piste cible et ajuste automatiquement la banque pour l'afficher"""
        tracks = list(self.song().tracks)
        if target_track in tracks:
            idx = tracks.index(target_track)
            target_bank = idx // NUM_TRACKS_PER_BANK
            if target_bank != self._current_bank_index:
                self._current_bank_index = target_bank
                self._send_bank_info()
            self.song().view.selected_track = target_track

    # =========================================================================
    # NAVIGATION DE BANQUES ET SÉLECTION DE PISTES
    # =========================================================================
    def _nav_bank_prev(self):
        if self._current_bank_index > 0:
            self._current_bank_index -= 1
            self._send_bank_info()
            self._send_bank_colors()

    def _nav_bank_next(self):
        total_tracks = len(self.song().tracks)
        total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
        if self._current_bank_index < total_banks - 1:
            self._current_bank_index += 1
            self._send_bank_info()
            self._send_bank_colors()

    def _select_track_in_bank(self, index_in_bank):
        """
        Sélectionne la piste ou le groupe correspondant.
        Si la piste cible est une Piste de Groupe (is_foldable) ET qu'elle est DÉJÀ sélectionnée,
        un second appui bascule l'état Déplié / Plié (Fold / Unfold) pour la clarté visuelle dans Ableton !
        """
        track_idx = (self._current_bank_index * NUM_TRACKS_PER_BANK) + index_in_bank
        tracks = self.song().tracks
        if 0 <= track_idx < len(tracks):
            target_track = tracks[track_idx]
            if target_track == self.song().view.selected_track and getattr(target_track, 'is_foldable', False):
                # Double appui sur un groupe -> Toggle Pliage / Dépliage
                try:
                    target_track.fold_state = not target_track.fold_state
                    self.log_message("LivePilot 16 : Toggle Fold Groupe : " + str(target_track.name))
                except Exception as e:
                    self.log_message("LivePilot 16 : Erreur fold_state : " + str(e))
            else:
                self.song().view.selected_track = target_track

    # =========================================================================
    # GESTION DES PARAMÈTRES & ÉCOUTEURS
    # =========================================================================
    def _attach_parameter_listeners(self):
        self._remove_parameter_listeners()
        if not self._current_device:
            return
        params = self._current_device.parameters[1:NUM_ENCODERS+1]
        for p in params:
            if not p.value_has_listener(self._on_parameter_value_changed):
                p.add_value_listener(self._on_parameter_value_changed)
                self._observed_params.append(p)

    def _remove_parameter_listeners(self):
        for p in self._observed_params:
            if p and p.value_has_listener(self._on_parameter_value_changed):
                p.remove_value_listener(self._on_parameter_value_changed)
        self._observed_params = []

    def _on_parameter_value_changed(self):
        self._send_parameters_info()

    def _adjust_parameter(self, encoder_idx, rel_value):
        """Ajustement relatif d'un paramètre (Twos Complement)"""
        if not self._current_device or encoder_idx >= NUM_ENCODERS:
            return
        params = self._current_device.parameters[1:NUM_ENCODERS+1]
        if encoder_idx < len(params):
            p = params[encoder_idx]
            step = (p.max - p.min) / 127.0
            new_val = p.value + (rel_value * step)
            p.value = max(p.min, min(p.max, new_val))

    # =========================================================================
    # GESTION MIDI ENTRANTE (Hardware -> Ableton)
    # =========================================================================
    def receive_midi(self, midi_bytes):
        """Réception et routage des messages MIDI du contrôleur physique"""
        if len(midi_bytes) < 3:
            return
        status, data1, data2 = midi_bytes[0], midi_bytes[1], midi_bytes[2]
        
        # Filtre sur les Control Change (Canal 1 : 0xB0)
        if (status & 0xF0) == 0xB0:
            cc_num = data1
            cc_val = data2
            
            # 1. Sélection de piste / groupe (Touches 1 à 16 : CC 64..79)
            if CC_BASE_TRACK_SEL <= cc_num < CC_BASE_TRACK_SEL + NUM_TRACKS_PER_BANK:
                if cc_val > 0:
                    self._select_track_in_bank(cc_num - CC_BASE_TRACK_SEL)
                    return
            
            # 2. Navigation Banque (TRACK - / TRACK +)
            elif cc_num == CC_NAV_TRACK_PREV and cc_val > 0:
                self._nav_bank_prev()
                return
            elif cc_num == CC_NAV_TRACK_NEXT and cc_val > 0:
                self._nav_bank_next()
                return

            # 3. Navigation Macro Groupes (GROUP - / GROUP +)
            elif cc_num == CC_NAV_GROUP_PREV and cc_val > 0:
                self._nav_group_prev()
                return
            elif cc_num == CC_NAV_GROUP_NEXT and cc_val > 0:
                self._nav_group_next()
                return
                
            # 4. Navigation Device sur la piste ou le groupe (DEVICE - / DEVICE + conditionnée à > 1)
            elif cc_num == CC_NAV_DEV_PREV and cc_val > 0:
                self._nav_device_prev()
                return
            elif cc_num == CC_NAV_DEV_NEXT and cc_val > 0:
                self._nav_device_next()
                return
                
            # 5. Rotation des 16 Encodeurs (CC 16..31)
            elif CC_BASE_ENCODERS <= cc_num < CC_BASE_ENCODERS + NUM_ENCODERS:
                delta = cc_val if cc_val < 64 else (cc_val - 128)
                self._adjust_parameter(cc_num - CC_BASE_ENCODERS, delta)
                return

            # 6. 17ᵉ Encodeur Master (CC 32) & Clic Poussoir (CC 33)
            elif cc_num == CC_ENC17_JOG:
                delta = cc_val if cc_val < 64 else (cc_val - 128)
                self._adjust_master_jog(delta)
                return
            elif cc_num == CC_ENC17_PUSH and cc_val > 0:
                self._toggle_master_mode()
                return

            # 7. Navigation Écran (Flèches ◄ / ►) & Bouton de Validation [VALID]
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

    # =========================================================================
    # ÉMISSION SYSEX (Ableton -> ESP32-S3)
    # =========================================================================
    def _full_resync(self):
        """Synchronisation globale initiale"""
        self._send_bank_info()
        self._send_bank_colors()
        self._send_scene_info()
        self._on_selected_track_changed()

    def _send_bank_info(self):
        """Envoie le numéro de banque active et le total de pistes"""
        total_tracks = len(self.song().tracks)
        total_banks = max(1, (total_tracks + NUM_TRACKS_PER_BANK - 1) // NUM_TRACKS_PER_BANK)
        sysex_msg = list(SYSEX_HEADER) + [CMD_BANK_INFO, self._current_bank_index, total_banks, total_tracks, 0xF7]
        self._send_midi(tuple(sysex_msg))

    def _send_bank_colors(self):
        """
        Envoie les couleurs RGB des 16 touches de la banque active.
        RÈGLE CLÉ : Si une piste (ou un groupe) est sélectionné mais SANS ASSIGNATION,
        sa couleur envoyée est BLANC PUR (127, 127, 127) !
        """
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
                    # PISTE OU GROUPE SÉLECTIONNÉ SANS ASSIGNATION -> BLANC PUR !
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
        """
        Envoie les métadonnées de la piste active.
        Inclut le flag is_group (1 si Piste de Groupe, 0 sinon) et has_assign_flag.
        """
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
            
        # Payload : CMD_TRACK_ACTIVE, track_index, has_assign_flag, is_group, ...name..., NULL, 0xF7
        sysex_msg = list(SYSEX_HEADER) + [CMD_TRACK_ACTIVE, track_index, has_assign_flag, is_group] + name_bytes + [0x00, 0xF7]
        self._send_midi(tuple(sysex_msg))

    def _send_active_device_info(self):
        """
        Envoie les infos du device actif sur la piste ou le groupe.
        RÈGLE CLÉ : nav_enabled vaut 1 UNIQUEMENT si total_assigned > 1 !
        """
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
        """Envoie les 16 paramètres du plugin actif sur la piste ou le bus de groupe"""
        if not self._current_device:
            # Envoie des paramètres vides pour effacer l'écran
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
        """
        Envoie les informations de la scène en cours de lecture et le tempo.
        - Ligne 1 Écran Gauche : Tempo affiché en haut à droite (ex: 126.0 BPM).
        - Ligne 2 Écran Gauche (Bandeau Scène Dédié Pleine Largeur) :
          Nom de la scène avec en fond d'écran la couleur exacte définie dans Ableton Live !
        """
        song = self.song()
        playing_scene = None
        playing_idx = 0
        
        # Recherche de la scène en cours de lecture
        for idx, sc in enumerate(song.scenes):
            if getattr(sc, 'is_playing', False):
                playing_scene = sc
                playing_idx = idx
                break
                
        # Si aucune scène ne joue explicitement, on prend la scène sélectionnée dans la vue
        is_playing = 1 if (playing_scene is not None and song.is_playing) else 0
        if not playing_scene:
            playing_scene = song.view.selected_scene
            try:
                playing_idx = list(song.scenes).index(playing_scene)
            except Exception:
                playing_idx = 0

        # Récupération de la couleur de la scène
        color_int = getattr(playing_scene, 'color', 0) if playing_scene else 0
        r = ((color_int >> 16) & 0xFF) >> 1
        g = ((color_int >> 8) & 0xFF) >> 1
        b = (color_int & 0xFF) >> 1

        # Récupération du tempo
        tempo = float(song.tempo)
        bpm_int = int(tempo)
        bpm_high = (bpm_int >> 7) & 0x7F
        bpm_low = bpm_int & 0x7F
        bpm_dec = int((tempo - bpm_int) * 10) & 0x7F

        # Nom de la scène (support étendu jusqu'à 96 caractères pour annotations scéniques)
        raw_name = playing_scene.name if (playing_scene and playing_scene.name) else ("Scene %d" % (playing_idx + 1))
        sc_name = raw_name[:96]
        name_bytes = [ord(c) & 0x7F for c in sc_name]

        # Payload SysEx : [CMD_SCENE_INFO, playing_idx, is_playing, bpm_high, bpm_low, bpm_dec, r, g, b, ...name..., 0x00, 0xF7]
        sysex_msg = list(SYSEX_HEADER) + [CMD_SCENE_INFO, playing_idx & 0x7F, is_playing, bpm_high, bpm_low, bpm_dec, r, g, b] + name_bytes + [0x00, 0xF7]
        self._send_midi(tuple(sysex_msg))

    # =========================================================================
    # 17ᵉ ENCODEUR MASTER & NAVIGATION ÉCRAN
    # =========================================================================
    def _adjust_master_jog(self, delta):
        """Ajuste le BPM en live ou navigue dans les scènes / paramètres"""
        if getattr(self, '_master_mode_bpm', True):
            new_tempo = max(20.0, min(999.0, self.song().tempo + delta))
            self.song().tempo = new_tempo
            self._send_scene_info()
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

    def _toggle_master_mode(self):
        """Bascule le mode du 17ᵉ encodeur (BPM live <-> Navigation scène/preset)"""
        self._master_mode_bpm = not getattr(self, '_master_mode_bpm', True)
        mode_str = "BPM" if self._master_mode_bpm else "SCENE"
        self.show_message("LivePilot 16 : Master Encoder 17 -> Mode " + mode_str)

    def _nav_screen_left(self):
        """Flèche Gauche ◄ : Scène précédente"""
        scenes = list(self.song().scenes)
        if scenes:
            try:
                cur_idx = scenes.index(self.song().view.selected_scene)
            except ValueError:
                cur_idx = 0
            if cur_idx > 0:
                self.song().view.selected_scene = scenes[cur_idx - 1]
                self._send_scene_info()

    def _nav_screen_right(self):
        """Flèche Droite ► : Scène suivante"""
        scenes = list(self.song().scenes)
        if scenes:
            try:
                cur_idx = scenes.index(self.song().view.selected_scene)
            except ValueError:
                cur_idx = 0
            if cur_idx < len(scenes) - 1:
                self.song().view.selected_scene = scenes[cur_idx + 1]
                self._send_scene_info()

    def _on_btn_valid_pressed(self):
        """Bouton [VALID] : Déclenche la scène sélectionnée ou valide l'action"""
        if self.song().view.selected_scene:
            self.song().view.selected_scene.fire()
            self._send_scene_info()


