/**
 * LivePilot Cockpit — Stage HUD Client Application v3.0
 * 16 Pistes (2 rangées de 8 - Copie conforme Launch Control XL)
 * 24 Knobs (3 rangées de 8) avec Numéro + Libellé assignation MIDI + Valeur
 * Top Bar : PLAY/PAUSE/STOP, Scène #, Track #, BPM, Scène 2 lignes, Master Volume Ableton
 * Sélecteur latéral de 4 Banques (1 à 4)
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
    masterVolume: {
      value: 0.85,
      str: '0.0 dB'
    },
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
    totalBanks: 4,
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
  const btnConfig = document.getElementById('btn-config');
  const configModal = document.getElementById('config-modal');
  const btnCloseConfig = document.getElementById('btn-close-config');
  const btnFullscreenToggle = document.getElementById('btn-fullscreen-toggle');
  const cfgConnStatus = document.getElementById('cfg-conn-status');

  // Top Bar : 4 Infos
  const playStatusBadge = document.getElementById('play-status-badge');
  const playStatusIcon = document.getElementById('play-status-icon');
  const playStatusText = document.getElementById('play-status-text');
  const sceneNumBadge = document.getElementById('scene-num-badge');
  const trackFocusPill = document.getElementById('track-focus-pill');
  const focusedTrackNum = document.getElementById('focused-track-num');
  const tempoDisplayEl = document.getElementById('tempo-display');

  // Scène Pleine Largeur (En cours & Suivante)
  const sceneActiveNum = document.getElementById('scene-active-num');
  const sceneActiveTitle = document.getElementById('scene-active-title');
  const sceneNextNum = document.getElementById('scene-next-num');
  const sceneNextTitle = document.getElementById('scene-next-title');
  const sceneFullBanner = document.getElementById('scene-full-banner');

  // Volume Général Ableton
  const masterVolText = document.getElementById('master-vol-text');
  const masterLedLadder = document.getElementById('master-led-ladder');
  const masterVolSlider = document.getElementById('master-vol-slider');

  // Banques & Grille 2x8
  const bankButtons = document.querySelectorAll('.bank-btn');
  const tracksRow1 = document.getElementById('tracks-row-1');
  const tracksRow2 = document.getElementById('tracks-row-2');

  // Device & Knobs
  const activeDeviceTitle = document.getElementById('active-device-title');
  const deviceChainBar = document.getElementById('device-chain-bar');
  const btnDevicePrev = document.getElementById('btn-device-prev');
  const btnDeviceNext = document.getElementById('btn-device-next');
  const btnDeviceSidePrev = document.getElementById('btn-device-side-prev');
  const btnDeviceSideNext = document.getElementById('btn-device-side-next');
  const devCounterNum = document.getElementById('dev-counter-num');

  const knobRows = [
    document.getElementById('knobs-row-1'),
    document.getElementById('knobs-row-2'),
    document.getElementById('knobs-row-3')
  ];

  // Scènes modal
  const scenesModal = document.getElementById('scenes-modal');
  const btnCloseScenes = document.getElementById('btn-close-scenes');
  const scenesList = document.getElementById('scenes-list');

  // Libellés d'assignation MIDI par défaut
  const defaultParamNames = [
    "Cutoff", "Resonance", "Drive", "Attack", "Decay", "Sustain", "Release", "Filter Env",
    "LFO Rate", "LFO Depth", "Send A", "Send B", "Send C", "Comp Thr", "Comp Ratio", "Dry/Wet",
    "Pan", "Width", "EQ Low", "EQ Mid", "EQ High", "Volume", "Limiter", "Master Glue"
  ];

  // --- INITIALISATION DU WEBSOCKET ---
  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      state.connected = true;
      if (cfgConnStatus) {
        cfgConnStatus.textContent = 'CONNECTÉ (LIVE ON AIR)';
        cfgConnStatus.className = 'config-badge-on';
      }
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      sendAction('request_full_sync');
      requestWakeLock();
    };

    ws.onclose = () => {
      state.connected = false;
      if (cfgConnStatus) {
        cfgConnStatus.textContent = 'DÉCONNECTÉ (OFFLINE)';
        cfgConnStatus.className = 'config-badge-off';
      }
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

  // --- GESTION DES MESSAGES DU SERVEUR ---
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
      case 'master_volume':
        updateMasterVolume(msg.data);
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
    if (data.master_volume) state.masterVolume = data.master_volume;
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

    renderTopBar();
    renderActiveScene();
    renderMasterVolume();
    renderBanks();
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
    renderTopBar();
  }

  function updateActiveScene(data) {
    state.activeScene = data;
    renderActiveScene();
    renderTopBar();
  }

  function updateSelectedTrack(data) {
    state.selectedTrackIndex = data.track_index;
    if (data.tracks) state.tracks = data.tracks;
    if (data.devices) state.devices = data.devices;
    if (data.active_device_name) state.activeDeviceName = data.active_device_name;
    if (data.active_device_index !== undefined) state.activeDeviceIndex = data.active_device_index;
    if (data.parameters) state.parameters = data.parameters;

    renderTopBar();
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

  function updateMasterVolume(data) {
    state.masterVolume = data;
    renderMasterVolume();
  }

  // --- RENDU UI : 4 INFOS TOP BAR ---
  function renderTopBar() {
    // 1. PLAY / PAUSE / STOP
    const status = state.playStatus || (state.isPlaying ? 'PLAY' : 'STOP');
    if (playStatusText) playStatusText.textContent = status;
    if (playStatusBadge) {
      if (status === 'PLAY') {
        playStatusBadge.className = 'status-pill play';
        if (playStatusIcon) playStatusIcon.textContent = '▶';
      } else if (status === 'PAUSE') {
        playStatusBadge.className = 'status-pill pause';
        if (playStatusIcon) playStatusIcon.textContent = '⏸';
      } else {
        playStatusBadge.className = 'status-pill stop';
        if (playStatusIcon) playStatusIcon.textContent = '⏹';
      }
    }

    // 2. TRACK SÉLECTIONNÉ
    const selTrack = state.tracks.find(t => t && t.index === state.selectedTrackIndex);
    const numFormatted = (state.selectedTrackIndex + 1) < 10 ? `0${state.selectedTrackIndex + 1}` : state.selectedTrackIndex + 1;
    if (trackFocusPill) {
      const lbl = trackFocusPill.querySelector('.pill-label');
      if (lbl) lbl.textContent = `TRACK #${numFormatted}`;
      if (focusedTrackNum) {
        focusedTrackNum.textContent = selTrack ? selTrack.name.toUpperCase() : `TRACK #${numFormatted}`;
      }
      if (selTrack && selTrack.is_group) {
        trackFocusPill.className = 'status-pill track-pill is-group';
      } else {
        trackFocusPill.className = 'status-pill track-pill';
      }
    }

    // 3. BPM
    if (tempoDisplayEl) tempoDisplayEl.textContent = `${state.tempo.toFixed(1)} BPM`;
  }

  // --- RENDU UI : BANDEAU DE SCÈNE PLEINE LARGEUR (EN COURS & SUIVANTE) ---
  function renderActiveScene() {
    const sc = state.activeScene || {};
    const curNum = sc.num || 1;
    const total = sc.total || 1;
    const curPrefix = curNum < 10 ? '0' + curNum : curNum;
    const rawCurName = sc.name || 'VERSE A (SYNTH & BASSLINE)';
    const curName = rawCurName.match(/^\d+/) ? rawCurName : `${curPrefix} - ${rawCurName} [${state.tempo.toFixed(0)} BPM]`;

    if (sceneActiveTitle) {
      sceneActiveTitle.textContent = curName;
    }

    // Scène suivante
    const nextNum = sc.next_num !== undefined ? sc.next_num : (curNum < total ? curNum + 1 : 0);
    const nextPrefix = nextNum < 10 ? '0' + nextNum : nextNum;
    const rawNextName = sc.next_name || (state.scenes && state.scenes[curNum] ? state.scenes[curNum].name : 'BUILDUP INTENSE DROPOUT (TRANSITION)');
    const nextName = nextNum > 0 ? (rawNextName.match(/^\d+/) ? rawNextName : `${nextPrefix} - ${rawNextName}`) : '--- FIN DU LIVE ---';

    if (sceneNextTitle) {
      sceneNextTitle.textContent = nextName;
    }
  }

  // --- RENDU UI : VOLUME GÉNÉRAL ABLETON (MASTER VOLUME AVEC VU-MÈTRE SEGMENTÉ) ---
  function renderMasterVolume() {
    const vol = state.masterVolume || { value: 0.85, str: '0.0 dB' };
    if (masterVolText) masterVolText.textContent = vol.str || '0.0 dB';
    
    if (masterLedLadder) {
      if (masterLedLadder.children.length === 0) {
        for (let s = 0; s < 16; s++) {
          const step = document.createElement('div');
          const colorClass = s < 11 ? 'green' : (s < 14 ? 'yellow' : 'red');
          step.className = `led-step ${colorClass}`;
          masterLedLadder.appendChild(step);
        }
      }
      const steps = masterLedLadder.children;
      const litCount = Math.round(Math.max(0, Math.min(1, vol.value)) * steps.length);
      for (let s = 0; s < steps.length; s++) {
        if (s < litCount) {
          steps[s].classList.add('active');
        } else {
          steps[s].classList.remove('active');
        }
      }
    }

    if (masterVolSlider && document.activeElement !== masterVolSlider) {
      masterVolSlider.value = vol.value;
    }
  }

  // --- RENDU UI : 4 BOUTONS DE SÉLECTION DE BANQUES ---
  function renderBanks() {
    bankButtons.forEach((btn, idx) => {
      if (idx === state.bankIndex) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });
  }

  // --- RENDU UI : LES 16 PISTES EN EXACTEMENT 8 COLONNES x 2 RANGÉES ---
  function renderTracks() {
    if (tracksRow1) tracksRow1.innerHTML = '';
    if (tracksRow2) tracksRow2.innerHTML = '';

    for (let i = 0; i < 16; i++) {
      const globalIndex = (state.bankIndex * 16) + i;
      const track = state.tracks[i] || {
        index: globalIndex,
        name: `TRK ${globalIndex + 1}`,
        color: '#444b60',
        is_group: false,
        fold_state: false,
        is_grouped: false,
        mute: false,
        solo: false,
        arm: false,
        vol_str: '-0.8 dB',
        pan_str: 'PAN C',
        pan_val: 0.0
      };

      const isSelected = (track.index === state.selectedTrackIndex);
      const isGroup = Boolean(track.is_group);
      const isGrouped = Boolean(track.is_grouped);
      const panVal = track.pan_val !== undefined ? track.pan_val : 0.0;
      const panStr = track.pan_str ? (track.pan_str.startsWith('PAN') ? track.pan_str : `PAN ${track.pan_str}`) : 'PAN C';
      const panPercent = Math.min(50, Math.round(Math.abs(panVal) * 50));
      const panDir = panVal < -0.01 ? 'left' : (panVal > 0.01 ? 'right' : 'center');
      const trackColor = track.color || (isGroup ? '#ffb703' : '#00f0ff');

      const strip = document.createElement('div');
      strip.id = `track-strip-${i}`;
      strip.className = `track-strip ${isSelected ? 'selected' : ''} ${isGroup ? 'is-group-bus' : ''}`;

      strip.innerHTML = `
        <div class="track-header-row">
          <div class="track-ch-badge-group">
            <span class="track-ch-badge">CH ${track.index + 1}</span>
            <div class="track-ch-color-line" style="background-color:${trackColor}"></div>
          </div>
          <div class="xl-button-housing">
            <span class="xl-btn-num" style="color:${trackColor}">${i + 1}</span>
          </div>
        </div>

        <div class="track-name-text" title="${track.name}">
          ${isGrouped ? '<span style="color:#7b88ab;margin-right:2px;">↳</span>' : ''}
          ${track.name}
        </div>

        <div class="track-pan-row" title="${panStr}">
          <span class="track-pan-label">${panStr}</span>
          <div class="pan-bipolar-track">
            <span class="pan-limit-lbl left">15L</span>
            <div class="pan-center-tick"></div>
            ${panDir !== 'center' ? `<div class="pan-fill-bar ${panDir}" style="width: ${panPercent}%;"></div>` : ''}
            <span class="pan-limit-lbl right">20R</span>
          </div>
        </div>

        <div class="track-bottom-row">
          <span class="track-vol-db">${track.vol_str || '-0.8 dB'}</span>
          <div class="meter-wrapper-inline">
            <div class="meter-bar-inline"><div class="meter-fill-inline meter-l" style="width:75%"></div></div>
            <div class="meter-bar-inline"><div class="meter-fill-inline meter-r" style="width:70%"></div></div>
          </div>
          <span class="track-mini-msa-tag">Mini M/S/A</span>
        </div>
      `;

      strip.addEventListener('click', (e) => {
        sendAction('select_track', { track_index: track.index });
      });

      if (i < 8) {
        if (tracksRow1) tracksRow1.appendChild(strip);
      } else {
        if (tracksRow2) tracksRow2.appendChild(strip);
      }
    }
  }

  // --- RENDU UI : CHAÎNE DE PLUGINS ---
  function renderDeviceChain() {
    if (activeDeviceTitle) activeDeviceTitle.textContent = state.activeDeviceName || '[2] Drum Buss (Master Bus Glue)';

    if (!deviceChainBar) return;
    deviceChainBar.innerHTML = '';

    if (!state.devices || state.devices.length === 0) {
      deviceChainBar.innerHTML = '<span class="device-pill active">PLUS</span><span class="device-pill active">DEVICE</span>';
      return;
    }

    state.devices.forEach((dev, idx) => {
      const pill = document.createElement('div');
      const isActive = idx === state.activeDeviceIndex;
      pill.className = `device-pill ${isActive ? 'active' : ''}`;
      pill.innerHTML = `<span>${dev.name || `DEV ${idx + 1}`}</span>`;
      pill.addEventListener('click', () => {
        sendAction('select_device', { device_index: idx });
      });
      deviceChainBar.appendChild(pill);
    });
  }

  // --- RENDU UI : 24 KNOBS (EXACTEMENT 8 COLONNES DE 3 RANGÉES) ---
  function renderKnobs() {
    knobRows.forEach(row => { if (row) row.innerHTML = ''; });

    for (let idx = 0; idx < 24; idx++) {
      const rowIndex = Math.floor(idx / 8);
      if (rowIndex > 2 || !knobRows[rowIndex]) continue;

      const param = state.parameters[idx] || {
        index: idx,
        name: defaultParamNames[idx] || `Param ${idx + 1}`,
        value: 0.5,
        str: '50 %'
      };

      const displayName = (param.name && param.name !== '-') ? param.name : (defaultParamNames[idx] || `Knob ${idx + 1}`);

      const card = document.createElement('div');
      card.id = `knob-card-${idx}`;
      card.className = 'knob-card';

      card.innerHTML = `
        <span class="knob-num-tag">#${idx + 1}</span>
        <div class="knob-svg-wrapper">
          ${renderKnobSvg(param.value, idx)}
        </div>
        <div class="knob-meta-info">
          <span class="knob-name-text" title="${displayName}">${displayName}</span>
          <span class="knob-val-text">${param.str || '-'}</span>
        </div>
      `;

      attachKnobInteraction(card, idx);
      knobRows[rowIndex].appendChild(card);
    }
  }

  function renderSingleKnob(idx) {
    const card = document.getElementById(`knob-card-${idx}`);
    if (!card) return;
    const param = state.parameters[idx];
    const valEl = card.querySelector('.knob-val-text');
    const svgWrap = card.querySelector('.knob-svg-wrapper');

    if (valEl) valEl.textContent = param.str || '-';
    if (svgWrap) svgWrap.innerHTML = renderKnobSvg(param.value, idx);

    card.classList.add('tweaked');
    setTimeout(() => card.classList.remove('tweaked'), 250);
  }

  function renderKnobSvg(normValue, idx = 0) {
    const val = Math.max(0, Math.min(1, normValue !== undefined ? normValue : 0.5));
    const startAngle = 135;
    const sweep = 270;
    const currentAngle = startAngle + val * sweep;

    const r = 13;
    const cx = 18;
    const cy = 18;

    const rad = (deg) => (deg * Math.PI) / 180;
    const x1 = cx + r * Math.cos(rad(startAngle));
    const y1 = cy + r * Math.sin(rad(startAngle));
    const x2 = cx + r * Math.cos(rad(currentAngle));
    const y2 = cy + r * Math.sin(rad(currentAngle));

    const largeArc = (val * sweep) > 180 ? 1 : 0;

    const needleR = 8.5;
    const nx = cx + needleR * Math.cos(rad(currentAngle));
    const ny = cy + needleR * Math.sin(rad(currentAngle));

    const bgArcD = `M ${cx + r * Math.cos(rad(135))} ${cy + r * Math.sin(rad(135))} A ${r} ${r} 0 1 1 ${cx + r * Math.cos(rad(405))} ${cy + r * Math.sin(rad(405))}`;
    const activeArcD = val > 0.01 ? `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}` : '';

    return `
      <svg viewBox="0 0 36 36" class="knob-svg" width="36" height="36" style="overflow:visible;display:block;">
        <defs>
          <filter id="glow-cyan-${idx}" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="0" stdDeviation="2" flood-color="#00f0ff" flood-opacity="0.85"/>
          </filter>
          <radialGradient id="knob-cap-grad" cx="40%" cy="40%" r="60%">
            <stop offset="0%" stop-color="#2c364d"/>
            <stop offset="70%" stop-color="#141824"/>
            <stop offset="100%" stop-color="#0b0d13"/>
          </radialGradient>
        </defs>
        <!-- Background track -->
        <path d="${bgArcD}" fill="none" stroke="#1d2538" stroke-width="2.8" stroke-linecap="round"/>
        <!-- Active cyan glowing arc -->
        ${activeArcD ? `<path d="${activeArcD}" fill="none" stroke="#00f0ff" stroke-width="3" stroke-linecap="round" filter="url(#glow-cyan-${idx})"/>` : ''}
        <!-- Dark Cap with bevel -->
        <circle cx="${cx}" cy="${cy}" r="9" fill="url(#knob-cap-grad)" stroke="#28344a" stroke-width="1.2"/>
        <!-- White needle indicator -->
        <line x1="${cx}" y1="${cy}" x2="${nx}" y2="${ny}" stroke="#ffffff" stroke-width="2" stroke-linecap="round"/>
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
      startVal = state.parameters[paramIdx] ? (state.parameters[paramIdx].value || 0) : 0.5;
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
    if (!scenesList) return;
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
        if (scenesModal) scenesModal.classList.add('hidden');
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

  // --- ÉCOUTEURS D'ÉVÉNEMENTS ---
  // Menu configuration
  if (btnConfig && configModal) {
    btnConfig.addEventListener('click', () => configModal.classList.remove('hidden'));
  }
  if (btnCloseConfig && configModal) {
    btnCloseConfig.addEventListener('click', () => configModal.classList.add('hidden'));
  }

  // Plein écran
  if (btnFullscreenToggle) {
    btnFullscreenToggle.addEventListener('click', () => {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    });
  }

  // Master Volume slider
  if (masterVolSlider) {
    masterVolSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      state.masterVolume.value = val;
      renderMasterVolume();
      sendAction('set_master_volume', { value: val });
    });
  }

  // 4 Boutons de sélection de Banque
  bankButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      const bankIdx = parseInt(btn.dataset.bank || '0', 10);
      sendAction('select_bank', { bank_index: bankIdx });
    });
  });

  // Navigation Device (Header + Sidebar)
  if (btnDevicePrev) btnDevicePrev.addEventListener('click', () => sendAction('nav_device_prev'));
  if (btnDeviceNext) btnDeviceNext.addEventListener('click', () => sendAction('nav_device_next'));
  if (btnDeviceSidePrev) btnDeviceSidePrev.addEventListener('click', () => sendAction('nav_device_prev'));
  if (btnDeviceSideNext) btnDeviceSideNext.addEventListener('click', () => sendAction('nav_device_next'));

  // Modale de scènes
  if (sceneFullBanner && scenesModal) {
    sceneFullBanner.addEventListener('click', () => scenesModal.classList.remove('hidden'));
  }
  if (btnCloseScenes && scenesModal) {
    btnCloseScenes.addEventListener('click', () => scenesModal.classList.add('hidden'));
  }

  connectWebSocket();
})();
