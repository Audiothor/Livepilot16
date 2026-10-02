/**
 * LivePilot Cockpit — Stage HUD Client Application v2.0
 * 16 Pistes (Miroir des 16 boutons Launch Control XL) + 24 Knobs (3x8)
 * Suivi précis de Scène sur 2 lignes et Focus Central de la piste active.
 */

(function () {
  'use strict';

  // --- ÉTAT LOCAL DE L'APPLICATION ---
  const state = {
    connected: false,
    tempo: 120.0,
    isPlaying: false,
    playStatus: 'STOP',
    position: '1.1.1',
    activeScene: {
      num: 1,
      total: 1,
      name: 'AUCUNE SCÈNE',
      desc: 'En attente de connexion Ableton Live...',
      color: '#1e2230',
      is_playing: false
    },
    scenes: [],
    bankIndex: 0,
    totalBanks: 1,
    selectedTrackIndex: 0,
    tracks: [],
    devices: [],
    activeDeviceIndex: 0,
    activeDeviceName: '[1/1] No Assignment',
    parameters: Array.from({ length: 24 }, (_, i) => ({
      index: i,
      name: `-`,
      value: 0.0,
      str: `-`,
      tweaked: false
    }))
  };

  let ws = null;
  let reconnectTimer = null;
  let wakeLock = null;

  // --- SÉLECTEURS DU DOM ---
  const statusBadge = document.getElementById('connection-status');
  const statusText = document.getElementById('status-text');
  const sceneNumBadge = document.getElementById('scene-num-badge');
  const sceneNameEl = document.getElementById('scene-name');
  const sceneDescEl = document.getElementById('scene-desc');
  const sceneBannerEl = document.getElementById('active-scene-banner');
  const positionCounterEl = document.getElementById('position-counter');
  const tempoDisplayEl = document.getElementById('tempo-display');
  const playStatusBadge = document.getElementById('play-status-badge');
  const playStatusIcon = document.getElementById('play-status-icon');
  const playStatusText = document.getElementById('play-status-text');
  const btnPlay = document.getElementById('btn-play');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnBankPrev = document.getElementById('btn-bank-prev');
  const btnBankNext = document.getElementById('btn-bank-next');
  const bankIndicator = document.getElementById('bank-indicator');
  const tracksContainer = document.getElementById('tracks-strip-container');
  const focusedTrackChip = document.getElementById('focused-track-chip');
  const focusedTrackVol = document.getElementById('focused-track-vol');
  const activeDeviceTitle = document.getElementById('active-device-title');
  const deviceChainBar = document.getElementById('device-chain-bar');
  const btnDevicePrev = document.getElementById('btn-device-prev');
  const btnDeviceNext = document.getElementById('btn-device-next');
  const scenesModal = document.getElementById('scenes-modal');
  const btnToggleScenes = document.getElementById('btn-toggle-scenes');
  const btnCloseScenes = document.getElementById('btn-close-scenes');
  const scenesList = document.getElementById('scenes-list');

  const knobRows = [
    document.getElementById('knobs-row-1'),
    document.getElementById('knobs-row-2'),
    document.getElementById('knobs-row-3')
  ];

  // --- INITIALISATION DU WEBSOCKET ---
  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      state.connected = true;
      statusBadge.className = 'status-badge connected';
      statusText.textContent = 'LIVE ON AIR';
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      sendAction('request_full_sync');
      requestWakeLock();
    };

    ws.onclose = () => {
      state.connected = false;
      statusBadge.className = 'status-badge disconnected';
      statusText.textContent = 'OFFLINE';
      if (!reconnectTimer) {
        reconnectTimer = setTimeout(connectWebSocket, 1500);
      }
    };

    ws.onerror = () => {
      ws.close();
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        handleServerMessage(msg);
      } catch (e) {
        console.error('Erreur parsing WS message:', e);
      }
    };
  }

  function sendAction(action, payload = {}) {
    if (ws && ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify({ action, ...payload }));
    }
  }

  // --- GESTION DES MESSAGES SERVEUR ---
  function handleServerMessage(msg) {
    switch (msg.type) {
      case 'full_sync':
        updateFullSync(msg.data);
        break;
      case 'meters':
        updateMeters(msg.data);
        break;
      case 'transport':
        updateTransport(msg.data);
        break;
      case 'scene':
        updateActiveScene(msg.data);
        break;
      case 'track_selected':
        updateSelectedTrack(msg.data);
        break;
      case 'device_selected':
        updateSelectedDevice(msg.data);
        break;
      case 'param_value':
        updateParamValue(msg.data);
        break;
      default:
        break;
    }
  }

  function updateFullSync(data) {
    if (data.tempo !== undefined) state.tempo = data.tempo;
    if (data.is_playing !== undefined) state.isPlaying = data.is_playing;
    if (data.play_status !== undefined) state.playStatus = data.play_status;
    if (data.position !== undefined) state.position = data.position;
    if (data.active_scene) state.activeScene = data.active_scene;
    if (data.scenes) state.scenes = data.scenes;
    if (data.bank_index !== undefined) state.bankIndex = data.bank_index;
    if (data.total_banks !== undefined) state.totalBanks = data.total_banks;
    if (data.tracks) state.tracks = data.tracks;
    if (data.selected_track_index !== undefined) state.selectedTrackIndex = data.selected_track_index;
    if (data.devices) state.devices = data.devices;
    if (data.active_device_index !== undefined) state.activeDeviceIndex = data.active_device_index;
    if (data.active_device_name !== undefined) state.activeDeviceName = data.active_device_name;
    if (data.parameters) state.parameters = data.parameters;

    renderTransport();
    renderActiveScene();
    renderTracks();
    renderDeviceChain();
    renderKnobs();
    renderScenesModal();
  }

  function updateMeters(meters) {
    if (!Array.isArray(meters)) return;
    meters.forEach((m, idx) => {
      const strip = document.getElementById(`track-strip-${idx}`);
      if (!strip) return;
      const fillL = strip.querySelector('.meter-l');
      const fillR = strip.querySelector('.meter-r');
      if (fillL && m.left !== undefined) fillL.style.width = `${Math.min(100, m.left * 100)}%`;
      if (fillR && m.right !== undefined) fillR.style.width = `${Math.min(100, m.right * 100)}%`;
    });
  }

  function updateTransport(data) {
    if (data.tempo !== undefined) state.tempo = data.tempo;
    if (data.is_playing !== undefined) state.isPlaying = data.is_playing;
    if (data.play_status !== undefined) state.playStatus = data.play_status;
    if (data.position !== undefined) state.position = data.position;
    renderTransport();
  }

  function updateActiveScene(data) {
    state.activeScene = data;
    renderActiveScene();
  }

  function updateSelectedTrack(data) {
    state.selectedTrackIndex = data.track_index;
    if (data.tracks) state.tracks = data.tracks;
    if (data.devices) state.devices = data.devices;
    if (data.active_device_name) state.activeDeviceName = data.active_device_name;
    if (data.active_device_index !== undefined) state.activeDeviceIndex = data.active_device_index;
    if (data.parameters) state.parameters = data.parameters;

    renderTracks();
    renderDeviceChain();
    renderKnobs();
  }

  function updateSelectedDevice(data) {
    state.activeDeviceIndex = data.device_index;
    state.activeDeviceName = data.device_name;
    if (data.parameters) state.parameters = data.parameters;
    renderDeviceChain();
    renderKnobs();
  }

  function updateParamValue(data) {
    const p = state.parameters[data.index];
    if (p) {
      p.value = data.value;
      p.str = data.str;
      renderSingleKnob(data.index);
    }
  }

  // --- RENDU UI : TRANSPORT & SCÈNE SUR 2 LIGNES ---
  function renderTransport() {
    tempoDisplayEl.textContent = state.tempo.toFixed(1);
    positionCounterEl.textContent = state.position;

    const status = state.playStatus || (state.isPlaying ? 'PLAY' : 'STOP');
    playStatusText.textContent = status;
    if (status === 'PLAY') {
      playStatusBadge.className = 'status-state-badge play';
      playStatusIcon.textContent = '▶';
      btnPlay.classList.add('active');
    } else if (status === 'PAUSE') {
      playStatusBadge.className = 'status-state-badge pause';
      playStatusIcon.textContent = '⏸';
      btnPlay.classList.remove('active');
    } else {
      playStatusBadge.className = 'status-state-badge stop';
      playStatusIcon.textContent = '⏹';
      btnPlay.classList.remove('active');
    }
  }

  function renderActiveScene() {
    const sc = state.activeScene || {};
    const num = sc.num || 1;
    const total = sc.total || 1;
    sceneNumBadge.textContent = `SCÈNE #${num}/${total}`;
    sceneNameEl.textContent = sc.name || 'AUCUNE SCÈNE';
    sceneDescEl.textContent = sc.desc || `Scène ${num} • Session Live`;

    if (sc.color && sc.color !== '#000000') {
      sceneBannerEl.style.backgroundColor = sc.color;
      sceneBannerEl.style.borderColor = '#ffffff';
      sceneBannerEl.style.color = '#ffffff';
    } else {
      sceneBannerEl.style.backgroundColor = '#1c202d';
      sceneBannerEl.style.borderColor = 'rgba(255,255,255,0.15)';
      sceneBannerEl.style.color = '#ffffff';
    }
  }

  // --- RENDU UI : LES 16 PISTES EN 2 RANGÉES DE 8 (DISPOSITION LAUNCH CONTROL XL) ---
  function renderTracks() {
    const startCh = (state.bankIndex * 16) + 1;
    const endCh = startCh + 15;
    bankIndicator.textContent = `BANQUE ${state.bankIndex + 1}/${state.totalBanks} (PISTES ${startCh}-${endCh})`;

    const tracksRow1 = document.getElementById('tracks-row-1');
    const tracksRow2 = document.getElementById('tracks-row-2');
    if (tracksRow1) tracksRow1.innerHTML = '';
    if (tracksRow2) tracksRow2.innerHTML = '';

    // Piste sélectionnée au centre
    const selTrack = state.tracks.find(t => t && t.index === state.selectedTrackIndex);
    if (selTrack) {
      const btnNum = (selTrack.index % 16) + 1;
      const bankNum = Math.floor(selTrack.index / 16) + 1;
      if (selTrack.is_group) {
        focusedTrackChip.textContent = `📁 GROUPE (BUS) : CH ${selTrack.index + 1} ★ ${selTrack.name.toUpperCase()} [${selTrack.fold_state ? 'PLIÉ 📁' : 'DÉPLIÉ 📂'}] (Bouton XL ${btnNum} • Banque ${bankNum})`;
        focusedTrackChip.style.color = '#ffcc00';
      } else if (selTrack.is_grouped) {
        focusedTrackChip.textContent = `CH ${selTrack.index + 1} ★ ${selTrack.name} (↳ ${selTrack.group_name || 'Groupe'}) (Bouton XL ${btnNum} • Banque ${bankNum})`;
        focusedTrackChip.style.color = selTrack.color || '#00f0ff';
      } else {
        focusedTrackChip.textContent = `CH ${selTrack.index + 1} ★ ${selTrack.name} (Bouton XL ${btnNum} • Banque ${bankNum})`;
        focusedTrackChip.style.color = selTrack.color || '#00f0ff';
      }
      focusedTrackVol.textContent = selTrack.vol_str || '0 dB';
    } else {
      const btnNum = (state.selectedTrackIndex % 16) + 1;
      const bankNum = Math.floor(state.selectedTrackIndex / 16) + 1;
      focusedTrackChip.textContent = `CH ${state.selectedTrackIndex + 1} (Bouton XL ${btnNum} • Banque ${bankNum})`;
      focusedTrackVol.textContent = '0 dB';
    }

    // Répartition 2x8 : Pistes 0-7 (Boutons 1-8) & Pistes 8-15 (Boutons 9-16)
    for (let i = 0; i < 16; i++) {
      const track = state.tracks[i] || {
        index: (state.bankIndex * 16) + i,
        name: `TRK ${(state.bankIndex * 16) + i + 1}`,
        color: '#444b60',
        is_group: false,
        fold_state: false,
        is_grouped: false,
        mute: false,
        solo: false,
        arm: false,
        vol_str: '-inf dB',
        pan_str: 'C'
      };

      const isSelected = (track.index === state.selectedTrackIndex);
      const isGroup = Boolean(track.is_group);
      const isGrouped = Boolean(track.is_grouped);

      const strip = document.createElement('div');
      strip.id = `track-strip-${i}`;
      strip.className = `track-strip ${isSelected ? 'selected' : ''} ${isGroup ? 'is-group-bus' : ''}`;

      strip.innerHTML = `
        <!-- Bouton physique avec barre LED horizontale (Miroir de la Photo 2) -->
        <div class="xl-button-housing">
          <div class="xl-led-bar" style="background-color:${track.color || '#555'}; color:${track.color || '#555'}"></div>
          <span class="xl-btn-num">${i + 1}</span>
        </div>

        <!-- Informations de la piste -->
        <div class="track-main-info">
          <div class="track-top-row">
            <span class="track-ch-badge">CH ${track.index + 1}${isSelected ? '★' : ''}</span>
            <span class="track-name-text" title="${track.name}">
              ${isGrouped ? '<span class="grouped-icon">↳</span>' : ''}
              ${track.name}
            </span>
            ${isGroup ? `<span class="group-pill">${track.fold_state ? '📁' : '📂'}</span>` : ''}
          </div>
          <div class="track-bottom-row">
            <span class="track-vol-db">${track.vol_str || '0 dB'}</span>
            <div class="meter-wrapper-inline">
              <div class="meter-bar-inline"><div class="meter-fill-inline meter-l"></div></div>
              <div class="meter-bar-inline"><div class="meter-fill-inline meter-r"></div></div>
            </div>
          </div>
        </div>

        <!-- Boutons d'action M/S/A -->
        <div class="track-actions-mini">
          <button class="btn-mini-act mute ${track.mute ? 'active' : ''}" data-track="${track.index}">M</button>
          <button class="btn-mini-act solo ${track.solo ? 'active' : ''}" data-track="${track.index}">S</button>
          <button class="btn-mini-act arm ${track.arm ? 'active' : ''}" data-track="${track.index}">A</button>
        </div>
      `;

      strip.addEventListener('click', (e) => {
        if (e.target.classList.contains('btn-mini-act')) return;
        sendAction('select_track', { track_index: track.index });
      });

      const btnMute = strip.querySelector('.btn-mini-act.mute');
      const btnSolo = strip.querySelector('.btn-mini-act.solo');
      const btnArm = strip.querySelector('.btn-mini-act.arm');

      btnMute.addEventListener('click', () => sendAction('toggle_mute', { track_index: track.index }));
      btnSolo.addEventListener('click', () => sendAction('toggle_solo', { track_index: track.index }));
      btnArm.addEventListener('click', () => sendAction('toggle_arm', { track_index: track.index }));

      if (i < 8) {
        if (tracksRow1) tracksRow1.appendChild(strip);
      } else {
        if (tracksRow2) tracksRow2.appendChild(strip);
      }
    }
  }

  // --- RENDU UI : CHAÎNE DE PLUGINS & NUMÉROTATION [2/3] ---
  function renderDeviceChain() {
    activeDeviceTitle.textContent = state.activeDeviceName || '[1/1] No Assignment';
    deviceChainBar.innerHTML = '';

    if (!state.devices || state.devices.length === 0) {
      deviceChainBar.innerHTML = '<span style="font-size:10px;color:#666;">Aucun plugin assigné</span>';
      return;
    }

    state.devices.forEach((dev, idx) => {
      const pill = document.createElement('div');
      const isActive = idx === state.activeDeviceIndex;
      pill.className = `device-pill ${isActive ? 'active' : ''}`;
      pill.innerHTML = `<span>${dev.label || `[${idx + 1}/${state.devices.length}] ${dev.name}`}</span>`;
      pill.addEventListener('click', () => {
        sendAction('select_device', { device_index: idx });
      });
      deviceChainBar.appendChild(pill);
    });
  }

  // --- RENDU UI : 24 KNOBS (3 RANGÉES DE 8 ALIGNÉES LAUNCH CONTROL XL) ---
  function renderKnobs() {
    knobRows.forEach(row => (row.innerHTML = ''));

    state.parameters.forEach((param, idx) => {
      const rowIndex = Math.floor(idx / 8);
      if (rowIndex > 2) return;

      const card = document.createElement('div');
      card.id = `knob-card-${idx}`;
      card.className = 'knob-card';

      card.innerHTML = `
        <div class="knob-name" title="${param.name}">${param.name || '-'}</div>
        <div class="knob-svg-wrapper">
          ${renderKnobSvg(param.value)}
        </div>
        <div class="knob-val-str">${param.str || '-'}</div>
      `;

      attachKnobInteraction(card, idx);
      knobRows[rowIndex].appendChild(card);
    });
  }

  function renderSingleKnob(idx) {
    const card = document.getElementById(`knob-card-${idx}`);
    if (!card) return;
    const param = state.parameters[idx];
    const nameEl = card.querySelector('.knob-name');
    const valEl = card.querySelector('.knob-val-str');
    const svgWrap = card.querySelector('.knob-svg-wrapper');

    if (nameEl) nameEl.textContent = param.name || '-';
    if (valEl) valEl.textContent = param.str || '-';
    if (svgWrap) svgWrap.innerHTML = renderKnobSvg(param.value);

    card.classList.add('tweaked');
    setTimeout(() => card.classList.remove('tweaked'), 300);
  }

  function renderKnobSvg(normValue) {
    const val = Math.max(0, Math.min(1, normValue || 0));
    const startAngle = 135;
    const endAngle = 405;
    const sweep = 270;
    const currentAngle = startAngle + val * sweep;

    const r = 15;
    const cx = 19;
    const cy = 19;

    const rad = (deg) => (deg * Math.PI) / 180;
    const x1 = cx + r * Math.cos(rad(startAngle));
    const y1 = cy + r * Math.sin(rad(startAngle));
    const x2 = cx + r * Math.cos(rad(currentAngle));
    const y2 = cy + r * Math.sin(rad(currentAngle));

    const largeArc = val * sweep > 180 ? 1 : 0;

    const bgArcD = `M ${cx + r * Math.cos(rad(135))} ${cy + r * Math.sin(rad(135))} A ${r} ${r} 0 1 1 ${cx + r * Math.cos(rad(405))} ${cy + r * Math.sin(rad(405))}`;
    const activeArcD = val > 0.01 ? `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}` : '';

    return `
      <svg viewBox="0 0 38 38" width="38" height="38">
        <path d="${bgArcD}" fill="none" stroke="#252a3b" stroke-width="3" stroke-linecap="round"/>
        ${activeArcD ? `<path d="${activeArcD}" fill="none" stroke="#00f0ff" stroke-width="3" stroke-linecap="round"/>` : ''}
        <line x1="${cx}" y1="${cy}" x2="${x2}" y2="${y2}" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
      </svg>
    `;
  }

  function attachKnobInteraction(card, paramIdx) {
    let startY = 0;
    let startVal = 0;
    let isDragging = false;

    const onStart = (clientY) => {
      isDragging = true;
      startY = clientY;
      startVal = state.parameters[paramIdx].value || 0;
    };

    const onMove = (clientY) => {
      if (!isDragging) return;
      const deltaY = startY - clientY;
      const newVal = Math.max(0, Math.min(1, startVal + deltaY / 150));
      sendAction('set_parameter', { index: paramIdx, value: newVal });
    };

    const onEnd = () => {
      isDragging = false;
    };

    card.addEventListener('mousedown', (e) => {
      onStart(e.clientY);
      const moveHandler = (ev) => onMove(ev.clientY);
      const upHandler = () => {
        onEnd();
        window.removeEventListener('mousemove', moveHandler);
        window.removeEventListener('mouseup', upHandler);
      };
      window.addEventListener('mousemove', moveHandler);
      window.addEventListener('mouseup', upHandler);
    });

    card.addEventListener('touchstart', (e) => {
      if (e.touches.length > 0) onStart(e.touches[0].clientY);
    }, { passive: true });

    card.addEventListener('touchmove', (e) => {
      if (e.touches.length > 0) onMove(e.touches[0].clientY);
    }, { passive: true });

    card.addEventListener('touchend', onEnd);
  }

  // --- RENDU UI : LISTE DES SCÈNES MODAL ---
  function renderScenesModal() {
    scenesList.innerHTML = '';
    state.scenes.forEach((sc) => {
      const card = document.createElement('div');
      card.className = `scene-item-card ${sc.is_playing ? 'playing' : ''}`;
      card.innerHTML = `
        <div class="scene-color-box" style="background-color: ${sc.color || '#555'}"></div>
        <span style="font-size:11px;font-weight:bold;">${sc.index + 1}. ${sc.name}</span>
      `;
      card.addEventListener('click', () => {
        sendAction('trigger_scene', { scene_index: sc.index });
        scenesModal.classList.add('hidden');
      });
      scenesList.appendChild(card);
    });
  }

  // --- SCREEN WAKE LOCK API ---
  async function requestWakeLock() {
    try {
      if ('wakeLock' in navigator) {
        wakeLock = await navigator.wakeLock.request('screen');
      }
    } catch (err) {
      console.warn('Wake Lock error:', err);
    }
  }

  document.addEventListener('visibilitychange', () => {
    if (wakeLock !== null && document.visibilityState === 'visible') {
      requestWakeLock();
    }
  });

  // --- LISTENERS ---
  btnPlay.addEventListener('click', () => sendAction('toggle_play'));
  document.getElementById('btn-tempo-down').addEventListener('click', () => sendAction('adjust_tempo', { delta: -1.0 }));
  document.getElementById('btn-tempo-up').addEventListener('click', () => sendAction('adjust_tempo', { delta: +1.0 }));
  btnBankPrev.addEventListener('click', () => sendAction('nav_bank_prev'));
  btnBankNext.addEventListener('click', () => sendAction('nav_bank_next'));
  btnDevicePrev.addEventListener('click', () => sendAction('nav_device_prev'));
  btnDeviceNext.addEventListener('click', () => sendAction('nav_device_next'));

  btnToggleScenes.addEventListener('click', () => scenesModal.classList.remove('hidden'));
  btnCloseScenes.addEventListener('click', () => scenesModal.classList.add('hidden'));

  btnFullscreen.addEventListener('click', () => {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(() => {});
    } else {
      document.exitFullscreen().catch(() => {});
    }
  });

  connectWebSocket();
})();
