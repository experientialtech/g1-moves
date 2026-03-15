#!/usr/bin/env node
/**
 * render_all_policies.js
 *
 * Renders hi-res policy preview videos from the MuJoCo WASM viewer
 * for all G1 Moves clips with trained policies.
 *
 * Usage:
 *   node render_all_policies.js                    # Render all
 *   node render_all_policies.js B_DadDance         # Render one clip
 *   node render_all_policies.js --skip-existing    # Skip already rendered
 *   node render_all_policies.js --list             # List all clips
 *
 * Requirements:
 *   - Chromium with --remote-debugging-port=9222
 *   - puppeteer-core, ffmpeg
 *   - HF CLI logged in (for upload)
 *
 * Pipeline per clip:
 *   1. Connect to Chromium via CDP
 *   2. Navigate to WASM viewer
 *   3. Wait for policy to load
 *   4. Wait for frame counter to reset to 0
 *   5. Screen-record full policy loop
 *   6. Crop to robot viewport (remove UI)
 *   7. Trim A-pose from start/end
 *   8. Upload to HF dataset + space
 */

const puppeteer = require('puppeteer-core');
const { execFileSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const http = require('http');

// ─── Config ──────────────────────────────────────────────────────────────────

const VIEWER_BASE = 'https://exptech-g1-moves.static.hf.space/viewer.html';
const CDP_URL = 'http://127.0.0.1:9222';
const CROP = { w: 780, h: 570, x: 72, y: 108 };
const TRIM_START = 3; // seconds to trim from start (A-pose)
const TRIM_END = 3;   // seconds to trim from end (A-pose)
const POLICY_FPS = 50; // policy runs at 50Hz
const SCREEN_SIZE = { w: 2560, h: 1440 };
const OUTPUT_DIR = '/tmp/policy-renders';
const LOG_FILE = path.join(OUTPUT_DIR, 'render.log');
const STATUS_FILE = path.join(OUTPUT_DIR, 'status.json');
const DASHBOARD_PORT = 3457;
const HF_REPO = 'exptech/g1-moves';

// ─── State ───────────────────────────────────────────────────────────────────

let status = {
  total: 0,
  completed: 0,
  failed: 0,
  skipped: 0,
  current: null,
  startTime: Date.now(),
  results: [],
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}`;
  console.log(line);
  fs.appendFileSync(LOG_FILE, line + '\n');
}

function updateStatus() {
  fs.writeFileSync(STATUS_FILE, JSON.stringify(status, null, 2));
}

async function loadClipList() {
  const dataPath = path.join(__dirname, 'public', 'data.json');
  if (fs.existsSync(dataPath)) {
    const data = JSON.parse(fs.readFileSync(dataPath, 'utf-8'));
    return data.clips || [];
  }
  // Fallback: fetch from HF
  log('Fetching clip list from HF...');
  const res = await fetch(`https://exptech-g1-moves.static.hf.space/data.json`);
  const data = await res.json();
  return data.clips || [];
}

function checkChromium() {
  return new Promise((resolve) => {
    const req = http.get(`${CDP_URL}/json/version`, (res) => {
      let body = '';
      res.on('data', d => body += d);
      res.on('end', () => resolve(true));
    });
    req.on('error', () => resolve(false));
    req.setTimeout(3000, () => { req.destroy(); resolve(false); });
  });
}

async function launchChromium(url) {
  log('Launching Chromium in kiosk mode...');
  const proc = spawn('google-chrome', [
    '--kiosk',
    '--remote-debugging-port=9222',
    '--no-first-run',
    '--disable-default-apps',
    url,
  ], { detached: true, stdio: 'ignore' });
  proc.unref();

  // Wait for CDP to be ready
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 1000));
    if (await checkChromium()) {
      log('Chromium ready');
      return proc;
    }
  }
  throw new Error('Chromium failed to start');
}

// ─── Core Pipeline ───────────────────────────────────────────────────────────

async function renderClip(clipId, category) {
  const viewerUrl = `${VIEWER_BASE}?clip=${encodeURIComponent(clipId)}&category=${encodeURIComponent(category)}`;
  const rawFile = path.join(OUTPUT_DIR, `${clipId}_raw.mp4`);
  const croppedFile = path.join(OUTPUT_DIR, `${clipId}_cropped.mp4`);
  const finalFile = path.join(OUTPUT_DIR, `${clipId}_policy.mp4`);

  log(`--- Rendering ${category}/${clipId} ---`);
  status.current = `${category}/${clipId}`;
  updateStatus();

  // 1. Connect to Chromium
  let browser;
  try {
    browser = await puppeteer.connect({ browserURL: CDP_URL });
  } catch (e) {
    // Launch Chromium if not running
    await launchChromium(viewerUrl);
    await new Promise(r => setTimeout(r, 5000));
    browser = await puppeteer.connect({ browserURL: CDP_URL });
  }

  const pages = await browser.pages();
  let page = pages[0];

  // 2. Navigate to viewer
  log(`Loading viewer: ${viewerUrl}`);
  await page.goto(viewerUrl, { waitUntil: 'networkidle0', timeout: 60000 });

  // 3. Wait for policy to load
  log('Waiting for policy to load...');
  try {
    await page.waitForSelector('#overlay.hidden', { timeout: 120000 });
  } catch (e) {
    log('ERROR: Policy failed to load (timeout)');
    await browser.disconnect();
    return { clipId, success: false, error: 'load_timeout' };
  }
  log('Policy loaded');

  // 4. Get total frames
  const totalFrames = await page.evaluate(() => {
    const all = document.body.innerText;
    const m = all.match(/Frame:\s*\d+\s*\/\s*(\d+)/);
    return m ? parseInt(m[1]) : null;
  });
  log(`Total frames: ${totalFrames}`);

  if (!totalFrames) {
    log('ERROR: Could not read frame count');
    await browser.disconnect();
    return { clipId, success: false, error: 'no_frames' };
  }

  // 4b. Hide ALL UI elements for clean recording — keep only the canvas
  await page.evaluate(() => {
    const style = document.createElement('style');
    style.textContent = `
      * { color: transparent !important; }
      button, a, nav, header, footer, .controls, .info, .hud,
      [class*="title"], [class*="header"], [class*="footer"],
      [class*="control"], [class*="button"], [class*="overlay"]:not(.hidden) {
        opacity: 0 !important;
        pointer-events: none !important;
      }
      canvas { color: initial !important; }
    `;
    document.head.appendChild(style);
  });

  // 5. Wait for frame to reset near 0
  log('Waiting for loop start...');
  let currentFrame = 999;
  let waitCount = 0;
  while (currentFrame > 10 && waitCount < 3000) {
    currentFrame = await page.evaluate(() => {
      const all = document.body.innerText;
      const m = all.match(/Frame:\s*(\d+)\s*\//);
      return m ? parseInt(m[1]) : 0;
    });
    await new Promise(r => setTimeout(r, 100));
    waitCount++;
  }
  log(`Starting at frame ${currentFrame}`);

  // 6. Calculate duration and record
  const durationS = Math.ceil(totalFrames / POLICY_FPS) + 4; // extra buffer
  log(`Recording for ${durationS}s...`);

  const ffmpegRec = spawn('ffmpeg', [
    '-y', '-f', 'x11grab',
    '-video_size', `${SCREEN_SIZE.w}x${SCREEN_SIZE.h}`,
    '-framerate', '30',
    '-i', ':0',
    '-t', String(durationS),
    '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
    rawFile,
  ], { stdio: ['pipe', 'pipe', 'pipe'] });

  await new Promise((resolve, reject) => {
    ffmpegRec.on('close', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`ffmpeg record exited ${code}`));
    });
    ffmpegRec.on('error', reject);
  });
  log('Recording complete');

  await browser.disconnect();

  // 7. Crop to robot viewport
  log('Cropping...');
  execFileSync('ffmpeg', [
    '-y', '-i', rawFile,
    '-vf', `crop=${CROP.w}:${CROP.h}:${CROP.x}:${CROP.y}`,
    '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
    croppedFile,
  ]);

  // 8. Trim A-pose
  const rawDuration = parseFloat(
    execFileSync('ffprobe', [
      '-v', 'quiet', '-show_entries', 'format=duration', '-of', 'csv=p=0', croppedFile,
    ]).toString().trim()
  );
  const trimmedDuration = rawDuration - TRIM_START - TRIM_END;

  if (trimmedDuration <= 0) {
    log('WARNING: Clip too short to trim, using full video');
    fs.copyFileSync(croppedFile, finalFile);
  } else {
    log(`Trimming: ${TRIM_START}s front, ${TRIM_END}s back (${trimmedDuration.toFixed(1)}s final)`);
    execFileSync('ffmpeg', [
      '-y', '-i', croppedFile,
      '-ss', String(TRIM_START), '-t', String(trimmedDuration),
      '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p',
      '-movflags', '+faststart', finalFile,
    ]);
  }

  // 9. Upload to HF
  log('Uploading to HF...');
  try {
    execFileSync('/home/mitch/.local/share/pipx/venvs/huggingface-hub/bin/python', ['-c', `
from huggingface_hub import HfApi
api = HfApi()
f = "${finalFile}"
api.upload_file(path_or_fileobj=f, path_in_repo="${category}/${clipId}/policy/${clipId}_policy.mp4", repo_id="${HF_REPO}", repo_type="dataset", commit_message="Hi-res ${clipId} policy render")
api.upload_file(path_or_fileobj=f, path_in_repo="media/${category}/${clipId}/policy/${clipId}_policy.mp4", repo_id="${HF_REPO}", repo_type="space", commit_message="Hi-res ${clipId} policy render")
print("uploaded")
`], { timeout: 300000 });
    log('Upload complete');
  } catch (e) {
    log(`Upload failed: ${e.message}`);
    return { clipId, success: false, error: 'upload_failed', file: finalFile };
  }

  // Cleanup raw/cropped
  try { fs.unlinkSync(rawFile); } catch {}
  try { fs.unlinkSync(croppedFile); } catch {}

  log(`Done: ${clipId}`);
  return { clipId, success: true, file: finalFile };
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

function startDashboard() {
  const server = http.createServer((req, res) => {
    const runtime = Math.floor((Date.now() - status.startTime) / 1000);
    const mins = Math.floor(runtime / 60);
    const secs = runtime % 60;
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({
      ...status,
      runtime: `${mins}m ${secs}s`,
      progress: `${status.completed + status.failed + status.skipped}/${status.total}`,
    }, null, 2));
  });
  server.listen(DASHBOARD_PORT, () => {
    log(`Dashboard: http://localhost:${DASHBOARD_PORT}`);
  });
  return server;
}

// ─── Main ────────────────────────────────────────────────────────────────────

async function main() {
  const args = process.argv.slice(2);
  const skipExisting = args.includes('--skip-existing');
  const listOnly = args.includes('--list');
  const singleClip = args.find(a => !a.startsWith('--'));

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });

  const allClips = await loadClipList();
  const policyClips = allClips.filter(c => c.has_onnx);

  if (listOnly) {
    console.log(`${policyClips.length} clips with policies:`);
    policyClips.forEach(c => console.log(`  ${c.category}/${c.id} (${c.frames} frames)`));
    return;
  }

  let clips = policyClips;
  if (singleClip) {
    clips = policyClips.filter(c => c.id === singleClip);
    if (clips.length === 0) {
      console.error(`Clip not found: ${singleClip}`);
      process.exit(1);
    }
  }

  status.total = clips.length;
  log(`Rendering ${clips.length} policy clips`);

  const dashboard = startDashboard();

  // Ensure Chromium is running
  if (!(await checkChromium())) {
    await launchChromium('about:blank');
  }

  for (const clip of clips) {
    const finalFile = path.join(OUTPUT_DIR, `${clip.id}_policy.mp4`);

    if (skipExisting && fs.existsSync(finalFile)) {
      log(`Skipping ${clip.id} (already exists)`);
      status.skipped++;
      updateStatus();
      continue;
    }

    try {
      const result = await renderClip(clip.id, clip.category);
      if (result.success) {
        status.completed++;
      } else {
        status.failed++;
      }
      status.results.push(result);
    } catch (e) {
      log(`FATAL ERROR on ${clip.id}: ${e.message}`);
      status.failed++;
      status.results.push({ clipId: clip.id, success: false, error: e.message });
    }
    updateStatus();

    // Brief pause between clips
    await new Promise(r => setTimeout(r, 2000));
  }

  log(`\n=== COMPLETE ===`);
  log(`Rendered: ${status.completed}, Failed: ${status.failed}, Skipped: ${status.skipped}`);

  const failures = status.results.filter(r => !r.success);
  if (failures.length > 0) {
    log('Failed clips:');
    failures.forEach(f => log(`  ${f.clipId}: ${f.error}`));
  }

  dashboard.close();
}

main().catch(e => {
  log(`Fatal: ${e.message}`);
  process.exit(1);
});
