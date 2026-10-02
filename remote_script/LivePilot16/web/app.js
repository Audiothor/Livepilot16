/**
 * LivePilot Cockpit — Stage HUD Client Application
 * WebSocket real-time bridge with Ableton Live Object Model (LOM)
 */

(function () {
  'use strict';

  // --- ÉTAT LOCAL DE L'APPLICATION ---
  const state = {
    connected: false,
    tempo: 120.0,
    isPlaying: false,
    position: '1.1.1',
    activeScene: { name: 'NO SCENE', color: '#1e2230' },
    scenes: [],
    bankIndex: 0,
    totalBanks: 1,
    selectedTrackIndex: 0,
    tracks: [],
    devices: [],
    activeDeviceIndex: 0,
    activeDeviceName: 'No Assignment',
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
  const sceneNameEl = document.getElementById('scene-name');
  const sceneBannerEl = document.getElementById('active-scene-banner');
  const positionCounterEl = document.getElementById('position-counter');
  const tempoDisplayEl = document.getElementById('tempo-display');
  const btnPlay = document.getElementById('btn-play');
  const btnFullscreen = document.getElementById('btn-fullscreen');
  const btnBankPrev = document.getElementById('btn-bank-prev');
  const btnBankNext = document.getElementById('btn-bank-next');
  const bankIndicator = document.getElementById('bank-indicator');
  const tracksContainer = document.getElementById('tracks-strip-container');
  const activeTrackNameEl = document.getElementById('active-track-name');
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
      const fillL = strip.querySelector('.meter-l .meter-fill');
      const fillR = strip.querySelector('.meter-r .meter-fill');
      if (fillL && m.left !== undefined) fillL.style.height = `${Math.min(100, m.left * 100)}%`;
      if (fillR && m.right !== undefined) fillR.style.height = `${Math.min(100, m.right * 100)}%`;
    });
  }

  function updateTransport(data) {
    if (data.tempo !== undefined) state.tempo = data.tempo;
    if (data.is_playing !== undefined) state.isPlaying = data.is_playing;
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

  // --- RENDU UI : TRANSPORT & SCÈNE ---
  function renderTransport() {
    tempoDisplayEl.textContent = state.tempo.toFixed(1);
    positionCounterEl.textContent = state.position;
    if (state.isPlaying) {
      btnPlay.classList.add('active');
    } else {
      btnPlay.classList.remove('active');
    }
  }

  function renderActiveScene() {
    sceneNameEl.textContent = state.activeScene.name || 'NO SCENE';
    if (state.activeScene.color) {
      sceneBannerEl.style.backgroundColor = state.activeScene.color;
      sceneBannerEl.style.borderColor = '#ffffff';
    } else {
      sceneBannerEl.style.backgroundColor = '#1e2230';
      sceneBannerEl.style.borderColor = 'rgba(255,255,255,0.1)';
    }
  }

  // --- RENDU UI : TRANCHES DE MIX (8 PISTES) ---
  function renderTracks() {
    bankIndicator.textContent = `BANK ${state.bankIndex + 1} / ${state.totalBanks}`;
    tracksContainer.innerHTML = '';

    const selTrack = state.tracks.find(t => t.index === state.selectedTrackIndex);
    if (selTrack) {
      activeTrackNameEl.textContent = selTrack.name;
    } else {
      activeTrackNameEl.textContent = '-';
    }

    for (let i = 0; i < 8; i++) {
      const track = state.tracks[i] || {
        index: -1,
        name: `TRK ${i + 1}`,
        color: '#333',
        is_group: false,
        mute: false,
        solo: false,
        arm: false,
        vol_str: '-inf dB',
        pan_str: 'C'
      };

      const isSelected = (track.index === state.selectedTrackIndex && track.index !== -1);
      const strip = document.createElement('div');
      strip.id = `track-strip-${i}`;
      strip.className = `track-strip ${isSelected ? 'selected' : ''}`;

      strip.innerHTML = `
        <div class="track-color-indicator" style="background-color: ${track.color || '#555'}"></div>
        <div class="track-header-box">
          <span class="track-num">CH ${track.index >= 0 ? track.index + 1 : i + 1}</span>
          <span class="track-name" title="${track.name}">${track.name} ${track.is_group ? '<span class="group-badge">GRP</span>' : ''}</span>
        </div>
        <div class="track-body">
          <div class="meter-wrapper">
            <div class="meter-bar meter-l"><div class="meter-fill"></div></div>
            <div class="meter-bar meter-r"><div class="meter-fill"></div></div>
          </div>
          <div class="fader-readout-box">
            <span class="fader-val">${track.vol_str || '-inf'}</span>
            <span class="pan-val">${track.pan_str || 'C'}</span>
          </div>
        </div>
        <div class="track-buttons">
          <button class="track-btn mute ${track.mute ? 'active' : ''}" data-track="${track.index}">M</button>
          <button class="track-btn solo ${track.solo ? 'active' : ''}" data-track="${track.index}">S</button>
          <button class="track-btn arm ${track.arm ? 'active' : ''}" data-track="${track.index}">A</button>
        </div>
      `;

      strip.addEventListener('click', (e) => {
        if (e.target.classList.contains('track-btn')) return;
        if (track.index >= 0) {
          sendAction('select_track', { track_index: track.index });
        }
      });

      // Boutons Mute, Solo, Arm
      const btnMute = strip.querySelector('.track-btn.mute');
      const btnSolo = strip.querySelector('.track-btn.solo');
      const btnArm = strip.querySelector('.track-btn.arm');

      btnMute.addEventListener('click', () => sendAction('toggle_mute', { track_index: track.index }));
      btnSolo.addEventListener('click', () => sendAction('toggle_solo', { track_index: track.index }));
      btnArm.addEventListener('click', () => sendAction('toggle_arm', { track_index: track.index }));

      tracksContainer.appendChild(strip);
    }
  }

  // --- RENDU UI : CHAÎNE DE PLUGINS / DEVICES ---
  function renderDeviceChain() {
    deviceChainBar.innerHTML = '';
    if (!state.devices || state.devices.length === 0) {
      deviceChainBar.innerHTML = '<span style="font-size:11px;color:#666;">No devices on track</span>';
      return;
    }

    state.devices.forEach((dev, idx) => {
      const pill = document.createElement('div');
      const isActive = idx === state.activeDeviceIndex;
      pill.className = `device-pill ${isActive ? 'active' : ''}`;
      pill.innerHTML = `<span>${dev.name}</span>`;
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

      // Interaction tactile ou glisser pour ajuster le paramètre
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

    const r = 18;
    const cx = 22;
    const cy = 22;

    const rad = (deg) => (deg * Math.PI) / 180;
    const x1 = cx + r * Math.cos(rad(startAngle));
    const y1 = cy + r * Math.sin(rad(startAngle));
    const x2 = cx + r * Math.cos(rad(currentAngle));
    const y2 = cy + r * Math.sin(rad(currentAngle));

    const largeArc = val * sweep > 180 ? 1 : 0;

    // Track de fond
    const bgArcD = `M ${cx + r * Math.cos(rad(135))} ${cy + r * Math.sin(rad(135))} A ${r} ${r} 0 1 1 ${cx + r * Math.cos(rad(405))} ${cy + r * Math.sin(rad(405))}`;
    // Arc actif
    const activeArcD = val > 0.01 ? `M ${x1} ${y1} A ${r} ${r} 0 ${largeArc} 1 ${x2} ${y2}` : '';

    return `
      <svg viewBox="0 0 44 44" width="44" height="44">
        <path d="${bgArcD}" fill="none" stroke="#252a3b" stroke-width="4" stroke-linecap="round"/>
        ${activeArcD ? `<path d="${activeArcD}" fill="none" stroke="#00f0ff" stroke-width="4" stroke-linecap="round"/>` : ''}
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
        <span style="font-size:12px;font-weight:bold;">${sc.index + 1}. ${sc.name}</span>
      `;
      card.addEventListener('click', () => {
        sendAction('trigger_scene', { scene_index: sc.index });
        scenesModal.classList.add('hidden');
      });
      scenesList.appendChild(card);
    });
  }

  // --- WAKE LOCK API (EMPECHE LA TABLETTE DE SE METTRE EN VEILLE SUR SCÈNE) ---
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

  // --- LISTENERS DES BOUTONS DE NAVIGATION & TRANSPORT ---
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

  // Démarrage initial
  connectWebSocket();
})();
