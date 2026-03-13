/* ========================================
   G1 Jukebox — Robot Remote Control App
   ======================================== */

(function () {
  'use strict';

  // ------------------------------------
  // Config
  // ------------------------------------
  const WS_PORT = 8080;
  const DATA_URL = 'data.json';
  const VIEWER_URL = 'viewer.html';

  // ------------------------------------
  // State
  // ------------------------------------
  let allClips = [];
  let baseUrl = '';
  let activeCategory = 'all';
  let selectedClip = null;
  let ws = null;
  let robotState = { status: 'idle', policy: null, message: 'Connecting...' };

  // ------------------------------------
  // DOM refs
  // ------------------------------------
  const grid = document.getElementById('policy-grid');
  const galleryView = document.getElementById('gallery-view');
  const remoteView = document.getElementById('remote-view');
  const connDot = document.getElementById('conn-dot');
  const statusBar = document.getElementById('status-bar');
  const statusIcon = document.getElementById('status-icon');
  const statusText = document.getElementById('status-text');
  const remoteTitle = document.getElementById('remote-title');
  const remoteMeta = document.getElementById('remote-meta');
  const remoteStatus = document.getElementById('remote-status');
  const remoteViewer = document.getElementById('remote-viewer');
  const btnLoad = document.getElementById('btn-load');
  const btnStart = document.getElementById('btn-start');
  const btnStop = document.getElementById('btn-stop');
  const backBtn = document.getElementById('back-btn');

  // ------------------------------------
  // Init
  // ------------------------------------
  async function init() {
    try {
      const res = await fetch(DATA_URL);
      const data = await res.json();
      allClips = data.clips.filter(c => c.has_policy && c.has_onnx);
      baseUrl = data.base_url;
      filterAndRender();
      setupFilters();
    } catch (err) {
      grid.innerHTML = '<p style="padding:2rem;color:#888;font-family:monospace;">Failed to load policy data</p>';
    }

    connectWebSocket();
    setupControls();

    // Listen for WASM viewer ready messages
    window.addEventListener('message', handleViewerMessage);
  }

  // ------------------------------------
  // WebSocket
  // ------------------------------------
  function connectWebSocket() {
    const wsUrl = 'ws://' + location.hostname + ':' + WS_PORT;
    try {
      ws = new WebSocket(wsUrl);
    } catch (e) {
      updateStatus('idle', 'WebSocket unavailable — UI only mode');
      return;
    }

    ws.onopen = function () {
      connDot.classList.add('connected');
      connDot.title = 'Connected';
      updateStatus('idle', 'Connected to robot');
    };

    ws.onmessage = function (e) {
      try {
        var msg = JSON.parse(e.data);
        if (msg.type === 'state') {
          robotState = msg;
          updateStatus(msg.status, msg.message);
          updateControlButtons();
        }
      } catch (err) { }
    };

    ws.onclose = function () {
      connDot.classList.remove('connected');
      connDot.title = 'Disconnected';
      updateStatus('idle', 'Disconnected — reconnecting...');
      setTimeout(connectWebSocket, 3000);
    };

    ws.onerror = function () {
      // Will trigger onclose
    };
  }

  function sendCommand(cmd, data) {
    if (!ws || ws.readyState !== WebSocket.OPEN) {
      // Offline mode — just update UI
      updateStatus('idle', 'Not connected to robot');
      return;
    }
    ws.send(JSON.stringify({ cmd: cmd, ...data }));
  }

  // ------------------------------------
  // Status
  // ------------------------------------
  function updateStatus(status, message) {
    statusBar.dataset.status = status;
    statusText.textContent = message || status;
  }

  function updateControlButtons() {
    var s = robotState.status;
    btnLoad.disabled = s === 'loading';
    btnStart.disabled = s === 'loading' || s === 'running' || (!robotState.policy && s !== 'stopped');
    btnStop.disabled = s !== 'running';
    btnStart.classList.toggle('active', s === 'running');

    // Update remote status text
    if (selectedClip && remoteView && !remoteView.classList.contains('hidden')) {
      remoteStatus.textContent = robotState.message || robotState.status;
    }
  }

  // ------------------------------------
  // Gallery
  // ------------------------------------
  function filterAndRender() {
    var clips = activeCategory === 'all'
      ? allClips.slice()
      : allClips.filter(function (c) { return c.category === activeCategory; });

    grid.innerHTML = '';

    clips.forEach(function (clip, i) {
      var card = createCard(clip);
      card.style.transitionDelay = (i * 0.03) + 's';
      grid.appendChild(card);

      // Trigger reveal
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          card.classList.add('visible');
        });
      });
    });

    observeLazy();
  }

  function createCard(clip) {
    var card = document.createElement('div');
    card.className = 'policy-card';
    card.dataset.clipId = clip.id;

    var viewerUrl = VIEWER_URL + '?clip=' + encodeURIComponent(clip.id) +
      '&category=' + encodeURIComponent(clip.category) + '&embed=1';

    // Get preview media
    var stageData = clip.stages.policy || clip.stages.training || clip.stages.retarget;
    var mediaSrc = stageData ? mediaUrl(stageData) : null;
    var isVideo = mediaSrc && mediaSrc.endsWith('.mp4');

    var mediaHtml = '';
    if (mediaSrc) {
      mediaHtml = isVideo
        ? '<video data-src="' + mediaSrc + '" autoplay muted loop playsinline preload="none" class="card-preview"></video>'
        : '<img data-src="' + mediaSrc + '" alt="' + esc(clip.name) + '" loading="lazy" class="card-preview">';
    }

    card.innerHTML =
      '<div class="card-media">' +
        mediaHtml +
        '<span class="card-category">' + clip.category + '</span>' +
        '<span class="card-badge">POLICY</span>' +
      '</div>' +
      '<div class="card-info">' +
        '<div class="card-title">' + esc(clip.name) + '</div>' +
        '<div class="card-performer">' + esc(clip.performer) + '</div>' +
      '</div>';

    card.addEventListener('click', function () {
      openRemote(clip);
    });

    return card;
  }

  // ------------------------------------
  // Lazy loading
  // ------------------------------------
  var lazyObserver = null;

  function observeLazy() {
    if (!lazyObserver) {
      lazyObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            var el = entry.target;
            if (el.dataset.src) {
              el.src = el.dataset.src;
            }
            lazyObserver.unobserve(el);
          }
        });
      }, { rootMargin: '200px' });
    }

    var els = grid.querySelectorAll('[data-src]');
    for (var i = 0; i < els.length; i++) {
      lazyObserver.observe(els[i]);
    }
  }

  // ------------------------------------
  // Viewer message handler (WASM ready)
  // ------------------------------------
  function handleViewerMessage(e) {
    if (!e.data || !e.data.clipId) return;

    // Gallery cards
    var card = grid.querySelector('.policy-card[data-clip-id="' + e.data.clipId + '"]');
    if (card) {
      if (e.data.type === 'viewer-status') {
        var statusEl = card.querySelector('.card-loading-status');
        if (statusEl) statusEl.textContent = e.data.status;
      }
      if (e.data.type === 'viewer-ready') {
        var iframe = card.querySelector('iframe.card-viewer-hidden');
        if (iframe) {
          iframe.classList.remove('card-viewer-hidden');
          iframe.classList.add('card-viewer-ready');
          var preview = card.querySelector('.card-preview');
          if (preview) preview.classList.add('card-preview-hidden');
        }
        var statusEl = card.querySelector('.card-loading-status');
        if (statusEl) statusEl.textContent = '';
      }
    }
  }

  // ------------------------------------
  // Filters
  // ------------------------------------
  function setupFilters() {
    var btns = document.querySelectorAll('.filter-btn');
    for (var i = 0; i < btns.length; i++) {
      btns[i].addEventListener('click', function () {
        for (var j = 0; j < btns.length; j++) btns[j].classList.remove('active');
        this.classList.add('active');
        activeCategory = this.dataset.category;
        filterAndRender();
      });
    }
  }

  // ------------------------------------
  // Remote Control
  // ------------------------------------
  function openRemote(clip) {
    selectedClip = clip;
    galleryView.classList.add('hidden');
    remoteView.classList.remove('hidden');

    remoteTitle.textContent = clip.name;
    remoteMeta.textContent = clip.category + '  ·  ' + clip.performer + '  ·  ' + formatDuration(clip.duration);
    remoteStatus.textContent = 'Ready';

    // Load WASM viewer in remote view
    var viewerUrl = VIEWER_URL + '?clip=' + encodeURIComponent(clip.id) +
      '&category=' + encodeURIComponent(clip.category) + '&embed=1';
    remoteViewer.innerHTML = '<iframe src="' + viewerUrl + '" allowtransparency="true"></iframe>';

    // Reset button states
    btnStart.disabled = true;
    btnStop.disabled = true;
    btnLoad.disabled = false;
    btnStart.classList.remove('active');

    window.scrollTo(0, 0);
  }

  function closeRemote() {
    selectedClip = null;
    remoteView.classList.add('hidden');
    galleryView.classList.remove('hidden');

    // Unload iframe
    var iframe = remoteViewer.querySelector('iframe');
    if (iframe) iframe.src = 'about:blank';
    remoteViewer.innerHTML = '';
  }

  // ------------------------------------
  // Controls
  // ------------------------------------
  function setupControls() {
    backBtn.addEventListener('click', closeRemote);

    btnLoad.addEventListener('click', function () {
      if (!selectedClip) return;
      sendCommand('load', { policy: selectedClip.id });
      remoteStatus.textContent = 'Loading ' + selectedClip.name + '...';
      btnLoad.disabled = true;
      btnStart.disabled = true;

      // In offline mode, simulate load
      if (!ws || ws.readyState !== WebSocket.OPEN) {
        setTimeout(function () {
          remoteStatus.textContent = selectedClip.name + ' loaded';
          btnLoad.disabled = false;
          btnStart.disabled = false;
          btnStop.disabled = true;
        }, 500);
      }
    });

    btnStart.addEventListener('click', function () {
      if (!selectedClip) return;
      sendCommand('start');
      remoteStatus.textContent = 'Playing ' + selectedClip.name;
      btnStart.disabled = true;
      btnStart.classList.add('active');
      btnStop.disabled = false;

      if (!ws || ws.readyState !== WebSocket.OPEN) {
        btnStart.disabled = true;
      }
    });

    btnStop.addEventListener('click', function () {
      if (!selectedClip) return;
      sendCommand('stop');
      remoteStatus.textContent = selectedClip.name + ' stopped';
      btnStart.disabled = false;
      btnStart.classList.remove('active');
      btnStop.disabled = true;

      if (!ws || ws.readyState !== WebSocket.OPEN) {
        // UI-only
      }
    });
  }

  // ------------------------------------
  // Utils
  // ------------------------------------
  function mediaUrl(stageData) {
    var file = stageData.mp4 || stageData.gif;
    if (!file) return null;
    return baseUrl ? baseUrl + '/' + file : file;
  }

  function formatDuration(seconds) {
    var m = Math.floor(seconds / 60);
    var s = Math.round(seconds % 60);
    return m + ':' + (s < 10 ? '0' : '') + s;
  }

  function esc(str) {
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  // ------------------------------------
  // Boot
  // ------------------------------------
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
