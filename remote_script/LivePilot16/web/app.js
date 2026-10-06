/**
 * LivePilot 16 — Live Control Cockpit Client Application
 * Layout strictly matching user-approved Stage HUD specifications
 * 16 Tracks (8x2), 24 Knobs (8x3), 3-Card Scene Banner, Master Output VU
 */

(function () {
  'use strict';

  // --- DEFAULT MOCK DATA ---
  const defaultTrackNames = [
    { num: '01', name: 'Drums', color: '#ff2a5f', dark: false, db: '-6.2 dB', pan: 50, lvlL: 68, lvlR: 72, isGroup: true },
    { num: '02', name: 'Bass', color: '#ffd000', dark: true, db: '-4.1 dB', pan: 50, lvlL: 78, lvlR: 78, isGroup: false },
    { num: '03', name: 'Pads', color: '#2979ff', dark: false, db: '-8.3 dB', pan: 50, lvlL: 55, lvlR: 58, isGroup: false },
    { num: '04', name: 'Lead', color: '#b388ff', dark: true, db: '-10.5 dB', pan: 50, lvlL: 48, lvlR: 45, isGroup: false },
    { num: '05', name: 'FX', color: '#00e676', dark: true, db: '-12.0 dB', pan: 50, lvlL: 42, lvlR: 40, isGroup: false },
    { num: '06', name: 'Vocals', color: '#ff4081', dark: false, db: '-7.1 dB', pan: 50, lvlL: 62, lvlR: 64, isGroup: false },
    { num: '07', name: 'Guitar', color: '#ff9100', dark: true, db: '-9.6 dB', pan: 50, lvlL: 52, lvlR: 50, isGroup: false },
    { num: '08', name: 'Keys', color: '#00e5ff', dark: true, db: '-11.4 dB', pan: 50, lvlL: 45, lvlR: 48, isGroup: false },
    { num: '09', name: 'Perc', color: '#7c4dff', dark: false, db: '-5.8 dB', pan: 50, lvlL: 70, lvlR: 68, isGroup: false },
    { num: '10', name: 'Stabs', color: '#76ff03', dark: true, db: '-14.1 dB', pan: 50, lvlL: 38, lvlR: 35, isGroup: false },
    { num: '11', name: 'Atmos', color: '#00b0ff', dark: true, db: '-11.2 dB', pan: 50, lvlL: 46, lvlR: 46, isGroup: false },
    { num: '12', name: 'Arp', color: '#f50057', dark: false, db: '-9.0 dB', pan: 50, lvlL: 54, lvlR: 56, isGroup: false },
    { num: '13', name: 'Brass', color: '#1de9b6', dark: true, db: '-16.3 dB', pan: 50, lvlL: 32, lvlR: 30, isGroup: false },
    { num: '14', name: 'Strings', color: '#ff6e40', dark: true, db: '-16.6 dB', pan: 50, lvlL: 30, lvlR: 32, isGroup: false },
    { num: '15', name: 'Synths', color: '#d500f9', dark: false, db: '-8.9 dB', pan: 50, lvlL: 56, lvlR: 60, isGroup: true },
    { num: '16', name: 'Vox FX', color: '#00bcd4', dark: true, db: '-12.7 dB', pan: 50, lvlL: 40, lvlR: 44, isGroup: false }
  ];

  const defaultTrackDevices = [
    { index: 0, num: '01', name: 'EQ Eight', type: 'EQ' },
    { index: 1, num: '02', name: 'Serum', type: 'SYNTH' },
    { index: 2, num: '03', name: 'Compressor', type: 'DYN' },
    { index: 3, num: '04', name: 'Echo', type: 'FX' },
    { index: 4, num: '05', name: 'Utility', type: 'UTIL' }
  ];

  const deviceParameterProfiles = {
    'EQ Eight': [
      { name: 'Low Cut', val: 0.20 },
      { name: 'Freq 1', val: 0.35 },
      { name: 'Gain 1', val: 0.52 },
      { name: 'Q 1', val: 0.45 },
      { name: 'Freq 2', val: 0.48 },
      { name: 'Gain 2', val: 0.42 },
      { name: 'Q 2', val: 0.50 },
      { name: 'Freq 3', val: 0.65 },
      { name: 'Gain 3', val: 0.60 },
      { name: 'Q 3', val: 0.55 },
      { name: 'Freq 4', val: 0.82 },
      { name: 'Gain 4', val: 0.48 },
      { name: 'Q 4', val: 0.40 },
      { name: 'High Cut', val: 0.88 }
    ],
    'Serum': [
      { name: 'Cutoff', val: 0.72 },
      { name: 'Resonance', val: 0.28 },
      { name: 'Drive', val: 0.54 },
      { name: 'Sub Level', val: 0.81 },
      { name: 'Noise', val: 0.23 },
      { name: 'FM Amount', val: 0.46 },
      { name: 'Osc Blend', val: 0.67 },
      { name: 'Pan', val: 0.50 },
      { name: 'Attack', val: 0.12 },
      { name: 'Decay', val: 0.58 },
      { name: 'Sustain', val: 0.76 },
      { name: 'Release', val: 0.34 },
      { name: 'Env Amount', val: 0.62 },
      { name: 'LFO 1 Rate', val: 0.48 },
      { name: 'LFO 1 Amt', val: 0.55 },
      { name: 'LFO 2 Rate', val: 0.39 },
      { name: 'LFO 2 Amt', val: 0.21 },
      { name: 'Warp', val: 0.66 },
      { name: 'Filter Env', val: 0.43 },
      { name: 'Unison', val: 0.75 },
      { name: 'Detune', val: 0.31 },
      { name: 'Width', val: 0.59 },
      { name: 'Delay Mix', val: 0.22 },
      { name: 'Reverb Mix', val: 0.68 }
    ],
    'Compressor': [
      { name: 'Threshold', val: 0.45 },
      { name: 'Ratio', val: 0.60 },
      { name: 'Attack', val: 0.25 },
      { name: 'Release', val: 0.40 },
      { name: 'Knee', val: 0.30 },
      { name: 'Dry/Wet', val: 0.85 },
      { name: 'Makeup', val: 0.55 },
      { name: 'Lookahead', val: 0.10 },
      { name: 'Sidechain', val: 0.00 },
      { name: 'SC Freq', val: 0.35 },
      { name: 'SC Gain', val: 0.50 },
      { name: 'SC Listen', val: 0.00 },
      { name: 'Peak/RMS', val: 0.70 },
      { name: 'Expander', val: 0.00 },
      { name: 'Auto Rel', val: 1.00 },
      { name: 'Gain Red', val: 0.38 }
    ],
    'Echo': [
      { name: 'Delay L', val: 0.38 },
      { name: 'Delay R', val: 0.45 },
      { name: 'Sync', val: 1.00 },
      { name: 'Feedback', val: 0.52 },
      { name: 'Dry/Wet', val: 0.40 },
      { name: 'Filter HP', val: 0.25 },
      { name: 'Filter LP', val: 0.75 },
      { name: 'Resonance', val: 0.30 },
      { name: 'Wobble', val: 0.45 },
      { name: 'Morph', val: 0.60 },
      { name: 'Noise', val: 0.15 },
      { name: 'Gate', val: 0.00 },
      { name: 'Reverb Mix', val: 0.35 },
      { name: 'Ducking', val: 0.20 },
      { name: 'Mod Depth', val: 0.55 },
      { name: 'Mod Rate', val: 0.40 },
      { name: 'Phase', val: 0.50 },
      { name: 'Stereo Mode', val: 1.00 },
      { name: 'Ping Pong', val: 1.00 },
      { name: 'Clipper', val: 0.30 }
    ],
    'Utility': [
      { name: 'Gain', val: 0.50 },
      { name: 'Pan', val: 0.50 },
      { name: 'Width', val: 0.80 },
      { name: 'Mute', val: 0.00 },
      { name: 'Phase L', val: 0.00 },
      { name: 'Phase R', val: 0.00 },
      { name: 'Bass Mono', val: 1.00 },
      { name: 'Mono Freq', val: 0.35 }
    ]
  };

  const defaultParamDefs = deviceParameterProfiles['Serum'];

  const knobColors = [
    '#ff4b72', '#ff7043', '#ffd54f', '#69f0ae', '#00e5ff', '#2979ff', '#b388ff', '#ff4081',
    '#ff5252', '#ffa726', '#ffca28', '#00e676', '#26c6da', '#42a5f5', '#9575cd', '#f06292',
    '#7e57c2', '#ff9800', '#ffeb3b', '#00e676', '#00bcd4', '#2196f3', '#673ab7', '#e91e63'
  ];

  // --- STATE ---
  const state = {
    connected: false,
    tempo: 120.0,
    signature: '4 / 4',
    isPlaying: false,
    playStatus: 'STOP',
    position: '1.1.1',
    masterVolume: { value: 0.82, str: '-0.2 dB' },
    activeScene: {
      num: 2,
      total: 12,
      name: '02 - Couplet',
      prev_num: 1,
      prev_name: '01 - Intro',
      next_num: 3,
      next_name: '03 - Refrain'
    },
    scenes: [],
    bankIndex: 0,
    totalBanks: 4,
    selectedTrackIndex: 1,
    tracks: [],
    devices: defaultTrackDevices,
    activeDeviceIndex: 1,
    activeDeviceName: 'Serum',
    parameters: Array.from({ length: 24 }, (_, i) => ({
      index: i,
      name: defaultParamDefs[i].name,
      value: defaultParamDefs[i].val,
      str: `${Math.round(defaultParamDefs[i].val * 100)} %`
    }))
  };

  let ws = null;
  let reconnectTimer = null;

  // --- WEBSOCKET CONNECTION ---
  function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      state.connected = true;
      const connEl = document.getElementById('connection-status');
      if (connEl) {
        connEl.className = 'connected-status';
        connEl.innerHTML = `
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M5 12.55a11 11 0 0 1 14.08 0"/>
            <path d="M1.42 9a16 16 0 0 1 21.16 0"/>
            <path d="M8.53 16.11a6 6 0 0 1 6.95 0"/>
            <circle cx="12" cy="20" r="1.5" fill="currentColor"/>
          </svg>
          Connected
        `;
      }
      if (reconnectTimer) {
        clearTimeout(reconnectTimer);
        reconnectTimer = null;
      }
      sendAction('request_full_sync');
    };

    ws.onclose = () => {
      state.connected = false;
      const connEl = document.getElementById('connection-status');
      if (connEl) {
        connEl.className = 'connected-status disconnected';
        connEl.innerHTML = `
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5">
            <line x1="1" y1="1" x2="23" y2="23"/>
            <path d="M16.72 11.06A10.94 10.94 0 0 1 19 12.55"/>
            <path d="M5 12.55a10.94 10.94 0 0 1 5.17-2.39"/>
            <path d="M1.42 9a15.91 15.91 0 0 1 4.7-2.88"/>
            <circle cx="12" cy="20" r="1.5" fill="currentColor"/>
          </svg>
          Disconnected
        `;
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

  // --- MESSAGE HANDLER ---
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
    if (data.signature) state.signature = data.signature;
    if (data.is_playing !== undefined) state.isPlaying = data.is_playing;
    if (data.play_status !== undefined) state.playStatus = data.play_status;
    if (data.active_scene) state.activeScene = data.active_scene;
    if (data.scenes) state.scenes = data.scenes;
    if (data.bank_index !== undefined) state.bankIndex = data.bank_index;
    if (data.total_banks !== undefined) state.totalBanks = data.total_banks;
    if (data.tracks) state.tracks = data.tracks;
    if (data.selected_track_index !== undefined) state.selectedTrackIndex = data.selected_track_index;
    if (data.devices) state.devices = data.devices;
    if (data.active_device_index !== undefined) state.activeDeviceIndex = data.active_device_index;
    if (data.active_device_name !== undefined) state.activeDeviceName = data.active_device_name;
    if (data.active_device_maker) state.activeDeviceMaker = data.active_device_maker;
    if (data.auto_follow !== undefined) state.autoFollow = data.auto_follow;
    if (data.master_volume) state.masterVolume = data.master_volume;
    if (data.parameters) state.parameters = data.parameters;

    renderTopBar();
    renderSceneBanner();
    renderTracks();
    renderKnobs();
    renderSidebar();
    renderMasterMeter();
  }

  function updateMeters(meters) {
    if (!Array.isArray(meters)) return;
    meters.forEach((m, idx) => {
      const card = document.getElementById(`track-card-${idx}`);
      if (!card) return;
      const barL = card.querySelector('.meter-gradient-fill.left');
      const barR = card.querySelector('.meter-gradient-fill.right');
      if (barL && m.left !== undefined) barL.style.width = `${Math.min(100, Math.round(m.left * 100))}%`;
      if (barR && m.right !== undefined) barR.style.width = `${Math.min(100, Math.round(m.right * 100))}%`;
    });
  }

  function updateTransport(data) {
    if (data.tempo !== undefined) state.tempo = data.tempo;
    if (data.is_playing !== undefined) state.isPlaying = data.is_playing;
    if (data.play_status !== undefined) state.playStatus = data.play_status;
    renderTopBar();
  }

  function updateActiveScene(data) {
    state.activeScene = data;
    renderSceneBanner();
  }

  function updateSelectedTrack(data) {
    state.selectedTrackIndex = data.track_index;
    if (data.tracks) state.tracks = data.tracks;
    if (data.devices && data.devices.length > 0) state.devices = data.devices;
    if (data.active_device_name) state.activeDeviceName = data.active_device_name;
    if (data.active_device_index !== undefined) state.activeDeviceIndex = data.active_device_index;
    if (data.parameters) state.parameters = data.parameters;

    renderTracks();
    renderKnobs();
    renderSidebar();
  }

  function updateSelectedDevice(data) {
    state.activeDeviceIndex = data.device_index;
    if (data.device_name) state.activeDeviceName = data.device_name;
    if (data.parameters) state.parameters = data.parameters;

    renderKnobs();
    renderSidebar();
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
    renderMasterMeter();
  }

  // --- RENDER TOP BAR ---
  function renderTopBar() {
    const bpmEl = document.getElementById('bpm-display');
    if (bpmEl) bpmEl.textContent = `${state.tempo.toFixed(0)} BPM`;

    const sigEl = document.getElementById('meter-signature');
    if (sigEl) sigEl.textContent = state.signature || '4 / 4';
  }

  // --- RENDER SCENE BANNER (AÉRÉ SANS TEXTES INUTILES) ---
  function renderSceneBanner() {
    const sc = state.activeScene || {};
    
    // Left (Previous)
    const prevTitle = document.getElementById('scene-prev-title');
    if (prevTitle) prevTitle.textContent = sc.prev_name || '01 - Intro';

    // Center (Active)
    const actTitle = document.getElementById('scene-active-title');
    if (actTitle) actTitle.textContent = sc.name || '02 - Couplet';

    // Right (Next)
    const nextTitle = document.getElementById('scene-next-title');
    if (nextTitle) nextTitle.textContent = sc.next_name || '03 - Refrain';
  }

  // --- RENDER TRACKS (16 Tracks: 8x2) ---
  function renderTracks() {
    const titleEl = document.getElementById('tracks-deck-title');
    if (titleEl) {
      const b = state.bankIndex + 1;
      const startTrk = (state.bankIndex * 16) + 1;
      const endTrk = (state.bankIndex + 1) * 16;
      titleEl.textContent = `PISTES (Banque ${b}/${state.totalBanks} : Pistes ${startTrk} - ${endTrk})`;
    }

    // Dynamic focus badge appended after parentheses
    const focusBadge = document.getElementById('tracks-current-focus-badge');
    const selGlobalIdx = state.selectedTrackIndex;
    const selNum = (selGlobalIdx + 1 < 10) ? `0${selGlobalIdx + 1}` : `${selGlobalIdx + 1}`;
    let selTrk = (state.tracks && state.tracks.length > 0)
      ? state.tracks.find(t => t && t.index === selGlobalIdx)
      : null;
    let selRawName = (selTrk && selTrk.name) ? selTrk.name : (defaultTrackNames[selGlobalIdx % 16] ? defaultTrackNames[selGlobalIdx % 16].name : `Piste ${selGlobalIdx + 1}`);
    const selCleanName = selRawName.replace(/^\d+[\s\-_:]+/, '');
    if (focusBadge) {
      focusBadge.textContent = `— Piste #${selNum} : ${selCleanName}`;
    }

    const bankInd = document.getElementById('bank-indicator');
    if (bankInd) bankInd.textContent = `Banque ${state.bankIndex + 1} / ${state.totalBanks}`;

    const container = document.getElementById('tracks-container');
    if (!container) return;
    container.innerHTML = '';

    for (let i = 0; i < 16; i++) {
      const globalIdx = (state.bankIndex * 16) + i;
      const defaultInfo = defaultTrackNames[i] || { name: `Track ${globalIdx + 1}`, color: '#2979ff', dark: false, db: '-6.0 dB', pan: 50, lvlL: 50, lvlR: 50, isGroup: false };
      
      // Recherche de la piste correspondante à cet emplacement global
      let trk = null;
      if (state.tracks && state.tracks.length > 0) {
        trk = state.tracks.find(t => t && t.index === globalIdx);
        if (!trk && state.tracks[i] && (state.tracks[i].index === undefined || state.tracks[i].index === globalIdx)) {
          trk = state.tracks[i];
        }
      }

      const trackIndex = (trk && trk.index !== undefined) ? trk.index : globalIdx;
      const trackNumber = trackIndex + 1;
      const trackNumStr = (trackNumber < 10) ? `0${trackNumber}` : `${trackNumber}`;

      let trackRawName = (trk && trk.name) ? trk.name : (state.bankIndex === 0 ? defaultInfo.name : `Track ${trackNumber}`);
      let trackCleanName = trackRawName.replace(/^\d+[\s\-_:]+/, '');

      const isSelected = (trackIndex === state.selectedTrackIndex);
      const isGroup = Boolean((trk && trk.is_group) || (state.bankIndex === 0 && defaultInfo.isGroup));
      const color = (trk && trk.color) ? trk.color : defaultInfo.color;
      const isDark = (color === '#ffd000' || color === '#76ff03' || color === '#00e5ff' || color === '#1de9b6');
      const textColor = isDark ? '#000000' : '#ffffff';

      const card = document.createElement('div');
      card.id = `track-card-${i}`;
      card.className = `track-card ${isSelected ? 'selected' : ''} ${isGroup ? 'is-group-track' : ''}`;

      const panDotLeft = 50 + (trk && trk.pan_val !== undefined ? trk.pan_val * 45 : 0);
      const grpBadge = isGroup ? `<span class="grp-tag-badge">GRP</span>` : '';

      card.innerHTML = `
        <div class="track-top-banner" style="background: ${color}; color: ${textColor};">
          <span class="trk-num">${trackNumStr}</span>
          <div class="trk-name">${grpBadge} <span>${trackCleanName}</span></div>
        </div>
        <div class="track-inner-body">
          <div class="meter-stereo-wrap">
            <div class="meter-channel-bar">
              <div class="meter-gradient-fill left" style="width: ${defaultInfo.lvlL}%;"></div>
              <div class="meter-tick-ref" style="left: 80%;"></div>
            </div>
            <div class="meter-channel-bar">
              <div class="meter-gradient-fill right" style="width: ${defaultInfo.lvlR}%;"></div>
              <div class="meter-tick-ref" style="left: 80%;"></div>
            </div>
            <div class="meter-scale-legend">
              <span>-∞</span>
              <span class="scale-ref-zero">0 dB</span>
              <span>+3</span>
            </div>
          </div>
          <div class="track-db-readout">${(trk && trk.vol_str) ? trk.vol_str : defaultInfo.db}</div>
          <div class="pan-line-wrap">
            <span>L</span>
            <div class="pan-track-line">
              <div class="pan-track-dot" style="left: calc(${panDotLeft}% - 2px);"></div>
            </div>
            <span>R</span>
          </div>
        </div>
      `;

      card.addEventListener('click', () => {
        state.selectedTrackIndex = trackIndex;
        renderTracks();
        renderSidebar();
        sendAction('select_track', { track_index: trackIndex });
      });

      container.appendChild(card);
    }
  }

  // --- RENDER 24 KNOBS (3 rows of 8) ---
  function renderKnobs() {
    // Dynamic Plugin Header
    const plugTitle = document.getElementById('plugin-deck-title');
    if (plugTitle) {
      const devs = (state.devices && state.devices.length > 0) ? state.devices : defaultTrackDevices;
      const totalDevs = devs.length;
      const curDev = state.activeDeviceIndex + 1;
      const curObj = devs[state.activeDeviceIndex];
      const devName = (curObj && curObj.name) ? curObj.name : (state.activeDeviceName || 'Serum');
      plugTitle.innerHTML = `PLUGIN &nbsp;—&nbsp; [${curDev}/${totalDevs}] ${devName}`;
    }

    const container = document.getElementById('knobs-container');
    if (!container) return;
    container.innerHTML = '';

    for (let i = 0; i < 24; i++) {
      const p = state.parameters[i];
      const isAssigned = Boolean(p && p.name && p.name !== '-' && p.name.trim() !== '' && p.name !== 'None' && p.is_assigned !== false);

      const cell = document.createElement('div');
      cell.id = `knob-cell-${i}`;

      if (isAssigned) {
        const color = knobColors[i % knobColors.length];
        cell.className = 'knob-cell';
        cell.innerHTML = `
          <span class="knob-index">${i + 1}</span>
          <div class="knob-svg-wrap">
            ${makeKnobSVG(p.value, color)}
          </div>
          <div class="knob-name">${p.name}</div>
          <div class="knob-value" style="color: ${color};">${p.str || `${Math.round(p.value * 100)} %`}</div>
        `;
        attachKnobDrag(cell, i);
      } else {
        cell.className = 'knob-cell unassigned';
        cell.innerHTML = `
          <span class="knob-index">${i + 1}</span>
          <div class="knob-svg-wrap">
            ${makeUnassignedKnobSVG()}
          </div>
          <div class="knob-name"></div>
          <div class="knob-value"></div>
        `;
      }

      container.appendChild(cell);
    }
  }

  function renderSingleKnob(i) {
    const cell = document.getElementById(`knob-cell-${i}`);
    if (!cell) return;
    const p = state.parameters[i];
    const isAssigned = Boolean(p && p.name && p.name !== '-' && p.name.trim() !== '' && p.name !== 'None' && p.is_assigned !== false);

    if (!isAssigned) {
      cell.className = 'knob-cell unassigned';
      const svgWrap = cell.querySelector('.knob-svg-wrap');
      if (svgWrap) svgWrap.innerHTML = makeUnassignedKnobSVG();
      const nameEl = cell.querySelector('.knob-name');
      if (nameEl) nameEl.textContent = '';
      const valEl = cell.querySelector('.knob-value');
      if (valEl) {
        valEl.textContent = '';
        valEl.style.color = 'transparent';
      }
      return;
    }

    cell.className = 'knob-cell';
    const color = knobColors[i % knobColors.length];

    const svgWrap = cell.querySelector('.knob-svg-wrap');
    if (svgWrap) svgWrap.innerHTML = makeKnobSVG(p.value, color);

    const nameEl = cell.querySelector('.knob-name');
    if (nameEl) nameEl.textContent = p.name;

    const valEl = cell.querySelector('.knob-value');
    if (valEl) {
      valEl.textContent = p.str || `${Math.round(p.value * 100)} %`;
      valEl.style.color = color;
    }
  }

  function makeUnassignedKnobSVG() {
    const r = 16;
    const cx = 21;
    const cy = 21;
    return `
      <svg viewBox="0 0 42 42" width="42" height="42">
        <circle cx="${cx}" cy="${cy}" r="${r - 3}" fill="#080c14" stroke="#121824" stroke-width="1.2"/>
        <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="#151e2e" stroke-width="2" stroke-dasharray="2 3"/>
      </svg>
    `;
  }

  function makeKnobSVG(val, color) {
    const r = 16;
    const cx = 21;
    const cy = 21;
    const startAngle = 225; // Départ à 7h30 (bas-gauche)
    const maxSweep = 270;   // Balayage horaire de 270° jusqu'à 4h30 (bas-droite)
    const currentSweep = Math.max(0.01, Math.min(1, val)) * maxSweep;

    const polarToCartesian = (centerX, centerY, radius, angleInDegrees) => {
      const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
      return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
      };
    };

    const describeArc = (x, y, radius, sAngle, sweep) => {
      const start = polarToCartesian(x, y, radius, sAngle);
      const end = polarToCartesian(x, y, radius, sAngle + sweep);
      const largeArc = sweep > 180 ? 1 : 0;
      return `M ${start.x.toFixed(2)} ${start.y.toFixed(2)} A ${radius} ${radius} 0 ${largeArc} 1 ${end.x.toFixed(2)} ${end.y.toFixed(2)}`;
    };

    const bgPath = describeArc(cx, cy, r, startAngle, maxSweep);
    const valPath = describeArc(cx, cy, r, startAngle, currentSweep);
    const tipPos = polarToCartesian(cx, cy, r, startAngle + currentSweep);

    return `
      <svg viewBox="0 0 42 42" width="42" height="42">
        <circle cx="${cx}" cy="${cy}" r="${r - 3}" fill="#0f1523" stroke="#161f31" stroke-width="1.2"/>
        <path d="${bgPath}" fill="none" stroke="#182338" stroke-width="3" stroke-linecap="round"/>
        <path d="${valPath}" fill="none" stroke="${color}" stroke-width="3" stroke-linecap="round" style="filter: drop-shadow(0 0 3px ${color});"/>
        <circle cx="${tipPos.x.toFixed(2)}" cy="${tipPos.y.toFixed(2)}" r="2" fill="${color}" style="filter: drop-shadow(0 0 2px ${color});"/>
      </svg>
    `;
  }

  function attachKnobDrag(el, idx) {
    let startY = 0;
    let startVal = 0;

    const onPointerMove = (e) => {
      const deltaY = startY - (e.clientY || (e.touches && e.touches[0].clientY));
      const deltaVal = deltaY / 120.0;
      let newVal = Math.max(0.0, Math.min(1.0, startVal + deltaVal));
      state.parameters[idx].value = newVal;
      state.parameters[idx].str = `${Math.round(newVal * 100)} %`;
      renderSingleKnob(idx);
      sendAction('set_param_value', { index: idx, value: newVal });
    };

    const onPointerUp = () => {
      window.removeEventListener('mousemove', onPointerMove);
      window.removeEventListener('mouseup', onPointerUp);
      window.removeEventListener('touchmove', onPointerMove);
      window.removeEventListener('touchend', onPointerUp);
    };

    el.addEventListener('mousedown', (e) => {
      startY = e.clientY;
      startVal = state.parameters[idx].value;
      window.addEventListener('mousemove', onPointerMove);
      window.addEventListener('mouseup', onPointerUp);
    });

    el.addEventListener('touchstart', (e) => {
      startY = e.touches[0].clientY;
      startVal = state.parameters[idx].value;
      window.addEventListener('touchmove', onPointerMove, { passive: false });
      window.addEventListener('touchend', onPointerUp);
    }, { passive: true });
  }

  // --- DEVICES / PLUGINS LIST (VERTICAL RECTANGLES) ---
  function renderDevicesList() {
    const container = document.getElementById('devices-list-container');
    if (!container) return;
    container.innerHTML = '';

    const devs = (state.devices && state.devices.length > 0) ? state.devices : defaultTrackDevices;

    devs.forEach((dev, idx) => {
      const isActive = (idx === state.activeDeviceIndex);
      const numStr = (idx + 1 < 10) ? `0${idx + 1}` : `${idx + 1}`;

      const item = document.createElement('div');
      item.className = `device-item-rect ${isActive ? 'active' : ''}`;
      item.id = `device-rect-${idx}`;

      item.innerHTML = `
        <div class="dev-item-left">
          <span class="dev-item-num">${numStr}</span>
          <span class="dev-item-name">${dev.name}</span>
        </div>
        ${isActive ? `<span class="dev-item-badge">ACTIF</span>` : ''}
      `;

      item.addEventListener('click', () => {
        selectDevice(idx);
      });

      container.appendChild(item);
    });

    updateDeviceNavButtons();
  }

  function updateDeviceNavButtons() {
    const devs = (state.devices && state.devices.length > 0) ? state.devices : defaultTrackDevices;
    const btnPrev = document.getElementById('btn-device-prev');
    const btnNext = document.getElementById('btn-device-next');

    if (btnPrev) {
      btnPrev.disabled = (state.activeDeviceIndex <= 0);
    }
    if (btnNext) {
      btnNext.disabled = (state.activeDeviceIndex >= devs.length - 1);
    }
  }

  function selectDevice(index) {
    const devs = (state.devices && state.devices.length > 0) ? state.devices : defaultTrackDevices;
    if (index < 0 || index >= devs.length) return;

    state.activeDeviceIndex = index;
    const targetDev = devs[index];
    state.activeDeviceName = targetDev.name;

    // Load parameters profile for this device
    const profile = deviceParameterProfiles[targetDev.name];
    if (profile) {
      state.parameters = Array.from({ length: 24 }, (_, i) => {
        if (i < profile.length) {
          return {
            index: i,
            name: profile[i].name,
            value: profile[i].val,
            str: profile[i].str || `${Math.round(profile[i].val * 100)} %`,
            is_assigned: true
          };
        } else {
          return {
            index: i,
            name: '-',
            value: 0.0,
            str: '-',
            is_assigned: false
          };
        }
      });
    } else {
      state.parameters = Array.from({ length: 24 }, (_, i) => ({
        index: i,
        name: `Param ${i + 1}`,
        value: 0.50,
        str: '50 %',
        is_assigned: true
      }));
    }

    renderKnobs();
    renderDevicesList();
    updateDeviceNavButtons();

    sendAction('select_device', { device_index: index });
  }

  // --- RENDER SIDEBAR ---
  function renderSidebar() {
    // 1. Selected Track Info (Point 1 : Toujours numéro de piste + nom)
    let selTrk = null;
    if (state.tracks && state.tracks.length > 0) {
      selTrk = state.tracks.find(t => t && t.index === state.selectedTrackIndex);
    }
    const selIdx = (selTrk && selTrk.index !== undefined) ? selTrk.index : state.selectedTrackIndex;
    const selNum = (selIdx + 1 < 10) ? `0${selIdx + 1}` : `${selIdx + 1}`;
    let trackRawName = (selTrk && selTrk.name) ? selTrk.name : (defaultTrackNames[selIdx % 16] ? defaultTrackNames[selIdx % 16].name : `Piste ${selIdx + 1}`);
    const trackCleanName = trackRawName.replace(/^\d+[\s\-_:]+/, '');
    const formattedTitle = `${selNum} - ${trackCleanName}`;

    const selName = document.getElementById('sel-track-name');
    if (selName) selName.textContent = formattedTitle;

    const trackColor = (selTrk && selTrk.color) ? selTrk.color : '#ffd000';
    const bar = document.getElementById('sel-accent-bar');
    if (bar) {
      bar.style.background = trackColor;
      bar.style.boxShadow = `0 0 6px ${trackColor}`;
    }

    // 2. Devices / Plugins List
    renderDevicesList();
  }

  // --- RENDER MASTER METER ---
  function renderMasterMeter() {
    const dbTag = document.getElementById('master-db-readout');
    const barL = document.getElementById('master-meter-l');
    const barR = document.getElementById('master-meter-r');
    const markerL = document.getElementById('master-fader-marker-l');
    const markerR = document.getElementById('master-fader-marker-r');
    const legendTxt = document.getElementById('master-fader-legend-txt');

    const vol = state.masterVolume || { value: 0.825, str: '-0.2 dB' };
    const str = vol.str || '-0.2 dB';
    if (dbTag) dbTag.innerHTML = `<span class="main-prefix">MAIN : </span>${str}`;
    if (legendTxt) legendTxt.textContent = `Fader : ${str}`;

    // Ableton 0 dB nominal corresponds to normalized value 0.85 (85%)
    // vol.value est entre 0.0 et 1.0 (0.85 = 0 dB, >0.85 = boost jusqu'à +6 dB)
    const faderPos = Math.min(100, Math.max(0, Math.round((vol.value !== undefined ? vol.value : 0.825) * 100)));
    if (markerL) markerL.style.left = `${faderPos}%`;
    if (markerR) markerR.style.left = `${faderPos}%`;

    // Niveaux audio instantanés (dynamiques ou simulés)
    const meterPct = Math.min(100, Math.max(0, Math.round(((vol.value || 0.825) * 0.98) * 100)));
    if (barL) barL.style.width = `${meterPct}%`;
    if (barR) barR.style.width = `${Math.max(0, meterPct - 2)}%`;
  }

  // --- EVENT LISTENERS INITIALIZATION ---
  function initListeners() {
    // Selected Track Navigation (◀ Piste précédente / Piste suivante ▶)
    const btnTrackPrev = document.getElementById('btn-track-prev');
    if (btnTrackPrev) {
      btnTrackPrev.addEventListener('click', (e) => {
        e.stopPropagation();
        const curIdx = state.selectedTrackIndex;
        const targetIdx = Math.max(0, curIdx - 1);
        state.selectedTrackIndex = targetIdx;
        renderTracks();
        renderSidebar();
        sendAction('select_track', { track_index: targetIdx });
      });
    }

    const btnTrackNext = document.getElementById('btn-track-next');
    if (btnTrackNext) {
      btnTrackNext.addEventListener('click', (e) => {
        e.stopPropagation();
        const curIdx = state.selectedTrackIndex;
        const maxIdx = (state.tracks && state.tracks.length > 0) ? state.tracks.length - 1 : 15;
        const targetIdx = Math.min(maxIdx, curIdx + 1);
        state.selectedTrackIndex = targetIdx;
        renderTracks();
        renderSidebar();
        sendAction('select_track', { track_index: targetIdx });
      });
    }
    // Scene navigation
    const btnScenePrev = document.getElementById('btn-scene-prev');
    if (btnScenePrev) {
      btnScenePrev.addEventListener('click', (e) => {
        e.stopPropagation();
        sendAction('fire_relative_scene', { offset: -1 });
      });
    }

    const prevCard = document.getElementById('scene-prev-card');
    if (prevCard) {
      prevCard.addEventListener('click', () => {
        sendAction('fire_relative_scene', { offset: -1 });
      });
    }

    const playBtn = document.getElementById('scene-play-btn');
    if (playBtn) {
      playBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        sendAction('toggle_play');
      });
    }

    const actCard = document.getElementById('scene-active-card');
    if (actCard) {
      actCard.addEventListener('click', () => {
        sendAction('fire_scene', { scene_index: (state.activeScene.num || 2) - 1 });
      });
    }

    const btnSceneNext = document.getElementById('btn-scene-next');
    if (btnSceneNext) {
      btnSceneNext.addEventListener('click', (e) => {
        e.stopPropagation();
        sendAction('fire_relative_scene', { offset: 1 });
      });
    }

    const nextCard = document.getElementById('scene-next-card');
    if (nextCard) {
      nextCard.addEventListener('click', () => {
        sendAction('fire_relative_scene', { offset: 1 });
      });
    }

    // Bank Navigation
    const btnBankPrev = document.getElementById('btn-bank-prev');
    if (btnBankPrev) {
      btnBankPrev.addEventListener('click', () => {
        const newBank = (state.bankIndex - 1 + state.totalBanks) % state.totalBanks;
        state.bankIndex = newBank;
        const bankStart = newBank * 16;
        const bankEnd = bankStart + 16;
        if (state.selectedTrackIndex < bankStart || state.selectedTrackIndex >= bankEnd) {
          state.selectedTrackIndex = bankStart;
        }
        sendAction('switch_bank', { bank: newBank, bank_index: newBank });
        sendAction('select_bank', { bank: newBank, bank_index: newBank });
        renderTracks();
        renderSidebar();
      });
    }

    const btnBankNext = document.getElementById('btn-bank-next');
    if (btnBankNext) {
      btnBankNext.addEventListener('click', () => {
        const newBank = (state.bankIndex + 1) % state.totalBanks;
        state.bankIndex = newBank;
        const bankStart = newBank * 16;
        const bankEnd = bankStart + 16;
        if (state.selectedTrackIndex < bankStart || state.selectedTrackIndex >= bankEnd) {
          state.selectedTrackIndex = bankStart;
        }
        sendAction('switch_bank', { bank: newBank, bank_index: newBank });
        sendAction('select_bank', { bank: newBank, bank_index: newBank });
        renderTracks();
        renderSidebar();
      });
    }

    // Device Navigation (◀ Précédent / Suivant ▶)
    const btnDevPrev = document.getElementById('btn-device-prev');
    if (btnDevPrev) {
      btnDevPrev.addEventListener('click', (e) => {
        e.stopPropagation();
        if (state.activeDeviceIndex > 0) {
          selectDevice(state.activeDeviceIndex - 1);
        }
      });
    }

    const btnDevNext = document.getElementById('btn-device-next');
    if (btnDevNext) {
      btnDevNext.addEventListener('click', (e) => {
        e.stopPropagation();
        const devs = (state.devices && state.devices.length > 0) ? state.devices : defaultTrackDevices;
        if (state.activeDeviceIndex < devs.length - 1) {
          selectDevice(state.activeDeviceIndex + 1);
        }
      });
    }
  }

  // --- START APP ---
  document.addEventListener('DOMContentLoaded', () => {
    try {
      const urlParams = new URLSearchParams(window.location.search);
      if (urlParams.has('bank')) {
        const b = parseInt(urlParams.get('bank'), 10);
        state.bankIndex = Math.max(0, Math.min(state.totalBanks - 1, b));
        state.selectedTrackIndex = state.bankIndex * 16;
      }
      if (urlParams.has('track')) {
        state.selectedTrackIndex = parseInt(urlParams.get('track'), 10);
        state.bankIndex = Math.floor(state.selectedTrackIndex / 16);
      }
      if (urlParams.has('device')) {
        const d = parseInt(urlParams.get('device'), 10);
        const devs = (state.devices && state.devices.length > 0) ? state.devices : defaultTrackDevices;
        if (d >= 0 && d < devs.length) {
          state.activeDeviceIndex = d;
          state.activeDeviceName = devs[d].name;
          const profile = deviceParameterProfiles[devs[d].name];
          if (profile) {
            state.parameters = Array.from({ length: 24 }, (_, i) => {
              if (i < profile.length) {
                return {
                  index: i,
                  name: profile[i].name,
                  value: profile[i].val,
                  str: profile[i].str || `${Math.round(profile[i].val * 100)} %`,
                  is_assigned: true
                };
              } else {
                return {
                  index: i,
                  name: '-',
                  value: 0.0,
                  str: '-',
                  is_assigned: false
                };
              }
            });
          }
        }
      }
    } catch (e) {
      // ignore
    }

    initListeners();
    renderTopBar();
    renderSceneBanner();
    renderTracks();
    renderKnobs();
    renderSidebar();
    renderMasterMeter();
    connectWebSocket();
  });

})();
