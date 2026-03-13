import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// ============================================================
// Constants
// ============================================================

const N_JOINTS = 29;
const OBS_DIM = 160;
const CONTROL_DT = 0.02; // 50 Hz policy, matching training (decimation=4, dt=0.005)
const MOTION_ANCHOR_IDX = 15; // torso_link in NPZ body array (0=pelvis, 15=torso)
const MUJOCO_ANCHOR_BODY = 16; // torso_link in MuJoCo xpos (0=world, 1=pelvis, 16=torso)

// Default joint positions (knees-bent keyframe) — XML joint order
const DEFAULT_JOINT_POS = new Float32Array([
  -0.312, 0, 0, 0.669, -0.363, 0,   // left leg: hip_pitch, hip_roll, hip_yaw, knee, ankle_pitch, ankle_roll
  -0.312, 0, 0, 0.669, -0.363, 0,   // right leg
  0, 0, 0,                           // waist: yaw, roll, pitch
  0.200, 0.200, 0, 0.600, 0, 0, 0,  // left arm: shoulder_pitch, shoulder_roll, shoulder_yaw, elbow, wrist_roll, wrist_pitch, wrist_yaw
  0.200, -0.200, 0, 0.600, 0, 0, 0  // right arm
]);

// Action scales per joint — XML joint order
const ACTION_SCALES = new Float32Array([
  0.5475, 0.3507, 0.5475, 0.3507, 0.4386, 0.4386,             // left leg
  0.5475, 0.3507, 0.5475, 0.3507, 0.4386, 0.4386,             // right leg
  0.5475, 0.4386, 0.4386,                                      // waist
  0.4386, 0.4386, 0.4386, 0.4386, 0.4386, 0.0745, 0.0745,     // left arm
  0.4386, 0.4386, 0.4386, 0.4386, 0.4386, 0.0745, 0.0745      // right arm
]);

// ============================================================
// Coordinate conversions (MuJoCo Z-up → Three.js Y-up)
// ============================================================

function getPosition(buffer, index, target) {
  return target.set(
    buffer[index * 3 + 0],
    buffer[index * 3 + 2],
   -buffer[index * 3 + 1]
  );
}

function getQuaternion(buffer, index, target) {
  return target.set(
   -buffer[index * 4 + 1],
   -buffer[index * 4 + 3],
    buffer[index * 4 + 2],
   -buffer[index * 4 + 0]
  );
}

// ============================================================
// Quaternion math (wxyz convention — MuJoCo native, no swizzle)
// ============================================================

function quatMul(a, b) {
  return [
    a[0]*b[0] - a[1]*b[1] - a[2]*b[2] - a[3]*b[3],
    a[0]*b[1] + a[1]*b[0] + a[2]*b[3] - a[3]*b[2],
    a[0]*b[2] - a[1]*b[3] + a[2]*b[0] + a[3]*b[1],
    a[0]*b[3] + a[1]*b[2] - a[2]*b[1] + a[3]*b[0]
  ];
}

function quatInv(q) {
  return [q[0], -q[1], -q[2], -q[3]];
}

function quatRotate(q, v) {
  const qv = quatMul(q, [0, v[0], v[1], v[2]]);
  const r = quatMul(qv, quatInv(q));
  return [r[1], r[2], r[3]];
}

function quatRotateInv(q, v) {
  return quatRotate(quatInv(q), v);
}

function quatToMat(q) {
  // Convert wxyz quaternion to 6D rotation representation matching training:
  // matrix_from_quat(q)[:,:,:2].reshape(-1,6) = row-major of (3,2) submatrix
  // Returns [R00, R01, R10, R11, R20, R21]
  const w = q[0], x = q[1], y = q[2], z = q[3];
  const x2 = x*x, y2 = y*y, z2 = z*z;
  const xy = x*y, xz = x*z, yz = y*z;
  const wx = w*x, wy = w*y, wz = w*z;
  return [
    1 - 2*(y2+z2), 2*(xy-wz),      // row 0: R[0,0], R[0,1]
    2*(xy+wz),     1 - 2*(x2+z2),  // row 1: R[1,0], R[1,1]
    2*(xz-wy),     2*(yz+wx)        // row 2: R[2,0], R[2,1]
  ];
}

// ============================================================
// NPZ parser (ZIP + numpy)
// ============================================================

async function loadNPZ(url) {
  const buf = await fetch(url).then(r => {
    if (!r.ok) throw new Error(`Failed to fetch ${url}: ${r.status}`);
    return r.arrayBuffer();
  });
  const bytes = new Uint8Array(buf);
  const entries = await parseZipEntries(bytes);
  const arrays = {};
  for (const [name, data] of Object.entries(entries)) {
    arrays[name.replace('.npy', '')] = parseNpy(data);
  }
  return arrays;
}

async function parseZipEntries(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const entries = {};
  let offset = 0;
  while (offset < bytes.length - 4) {
    const sig = view.getUint32(offset, true);
    if (sig !== 0x04034b50) break;
    const method = view.getUint16(offset + 8, true);
    let compSize = view.getUint32(offset + 18, true);
    let uncompSize = view.getUint32(offset + 22, true);
    const nameLen = view.getUint16(offset + 26, true);
    const extraLen = view.getUint16(offset + 28, true);
    const name = new TextDecoder().decode(bytes.slice(offset + 30, offset + 30 + nameLen));

    // Handle ZIP64 extra field (sizes = 0xFFFFFFFF)
    if (compSize === 0xFFFFFFFF || uncompSize === 0xFFFFFFFF) {
      const extraStart = offset + 30 + nameLen;
      let eOff = 0;
      while (eOff + 4 <= extraLen) {
        const hid = view.getUint16(extraStart + eOff, true);
        const hsz = view.getUint16(extraStart + eOff + 2, true);
        if (hid === 0x0001 && hsz >= 16) {
          // ZIP64: 8-byte uncompressed, 8-byte compressed
          const lo0 = view.getUint32(extraStart + eOff + 4, true);
          const hi0 = view.getUint32(extraStart + eOff + 8, true);
          const lo1 = view.getUint32(extraStart + eOff + 12, true);
          const hi1 = view.getUint32(extraStart + eOff + 16, true);
          uncompSize = lo0 + hi0 * 0x100000000;
          compSize = lo1 + hi1 * 0x100000000;
          break;
        }
        eOff += 4 + hsz;
      }
    }

    const dataStart = offset + 30 + nameLen + extraLen;
    let fileData;
    if (method === 0) {
      fileData = bytes.slice(dataStart, dataStart + uncompSize);
    } else if (method === 8) {
      fileData = await decompressRaw(bytes.slice(dataStart, dataStart + compSize));
    } else {
      throw new Error(`Unsupported ZIP method: ${method}`);
    }
    entries[name] = fileData;
    offset = dataStart + compSize;
  }
  return entries;
}

function decompressRaw(compressed) {
  const ds = new DecompressionStream('deflate-raw');
  const writer = ds.writable.getWriter();
  const reader = ds.readable.getReader();
  writer.write(compressed);
  writer.close();
  const chunks = [];
  return new Promise((resolve, reject) => {
    (function pump() {
      reader.read().then(({ done, value }) => {
        if (done) {
          const total = chunks.reduce((s, c) => s + c.length, 0);
          const result = new Uint8Array(total);
          let off = 0;
          for (const c of chunks) { result.set(c, off); off += c.length; }
          resolve(result);
        } else {
          chunks.push(value);
          pump();
        }
      }).catch(reject);
    })();
  });
}

function parseNpy(bytes) {
  const major = bytes[6];
  let headerLen, headerOffset;
  if (major <= 1) {
    headerLen = new DataView(bytes.buffer, bytes.byteOffset + 8, 2).getUint16(0, true);
    headerOffset = 10;
  } else {
    headerLen = new DataView(bytes.buffer, bytes.byteOffset + 8, 4).getUint32(0, true);
    headerOffset = 12;
  }
  const headerStr = new TextDecoder().decode(bytes.slice(headerOffset, headerOffset + headerLen));
  const shapeMatch = headerStr.match(/'shape':\s*\(([^)]*)\)/);
  const descrMatch = headerStr.match(/'descr':\s*'([^']*)'/);
  const shape = shapeMatch[1].split(',').filter(s => s.trim()).map(s => parseInt(s.trim()));
  const dtype = descrMatch[1];
  const dataStart = headerOffset + headerLen;

  // Compute expected element count from shape
  const numElements = shape.length > 0 ? shape.reduce((a, b) => a * b, 1) : 1;
  const bytesPerElement = dtype === '<f8' ? 8 : 4;
  const expectedBytes = numElements * bytesPerElement;

  // Copy exactly the expected number of bytes for proper alignment
  const rawBytes = bytes.slice(dataStart, dataStart + expectedBytes);
  const ab = rawBytes.buffer.slice(rawBytes.byteOffset, rawBytes.byteOffset + rawBytes.byteLength);
  if (dtype === '<f4') return { shape, data: new Float32Array(ab) };
  if (dtype === '<f8') return { shape, data: new Float64Array(ab) };
  if (dtype === '<i4') return { shape, data: new Int32Array(ab) };
  throw new Error(`Unsupported numpy dtype: ${dtype}`);
}

// ============================================================
// Three.js scene builder from MuJoCo model
// ============================================================

function buildSceneFromModel(mujoco, model, data) {
  const bodies = {};
  const meshCache = {};

  for (let g = 0; g < model.ngeom; g++) {
    if (!(model.geom_group[g] < 3)) continue;

    const b = model.geom_bodyid[g];
    const type = model.geom_type[g];
    const size = [
      model.geom_size[g * 3 + 0],
      model.geom_size[g * 3 + 1],
      model.geom_size[g * 3 + 2]
    ];

    if (!(b in bodies)) {
      bodies[b] = new THREE.Group();
      bodies[b].name = `body_${b}`;
      bodies[b].bodyID = b;
    }

    let geometry;

    if (type === 0) { // plane
      geometry = new THREE.PlaneGeometry(100, 100);
    } else if (type === 2) { // sphere
      geometry = new THREE.SphereGeometry(size[0], 16, 16);
    } else if (type === 3) { // capsule
      geometry = new THREE.CapsuleGeometry(size[0], size[1] * 2, 12, 16);
    } else if (type === 5) { // cylinder
      geometry = new THREE.CylinderGeometry(size[0], size[0], size[1] * 2, 16);
    } else if (type === 6) { // box
      geometry = new THREE.BoxGeometry(size[0] * 2, size[2] * 2, size[1] * 2);
    } else if (type === 7) { // mesh
      const meshID = model.geom_dataid[g];
      if (meshID < 0) continue;

      if (meshID in meshCache) {
        geometry = meshCache[meshID];
      } else {
        geometry = new THREE.BufferGeometry();

        const vertBuf = model.mesh_vert.subarray(
          model.mesh_vertadr[meshID] * 3,
          (model.mesh_vertadr[meshID] + model.mesh_vertnum[meshID]) * 3
        );
        // Swizzle vertices: (x, y, z) → (x, z, -y) for Three.js Y-up
        for (let v = 0; v < vertBuf.length; v += 3) {
          const tmp = vertBuf[v + 1];
          vertBuf[v + 1] = vertBuf[v + 2];
          vertBuf[v + 2] = -tmp;
        }

        const faceVerts = model.mesh_face.subarray(
          model.mesh_faceadr[meshID] * 3,
          (model.mesh_faceadr[meshID] + model.mesh_facenum[meshID]) * 3
        );

        geometry.setAttribute('position', new THREE.BufferAttribute(vertBuf, 3));
        geometry.setIndex(Array.from(faceVerts));
        geometry.computeVertexNormals();
        meshCache[meshID] = geometry;
      }
    } else {
      continue;
    }

    if (!geometry) continue;

    const color = [
      model.geom_rgba[g * 4 + 0],
      model.geom_rgba[g * 4 + 1],
      model.geom_rgba[g * 4 + 2],
      model.geom_rgba[g * 4 + 3]
    ];

    // Check for material
    let matColor = color;
    let texture;
    if (model.geom_matid[g] !== -1) {
      const matId = model.geom_matid[g];
      matColor = [
        model.mat_rgba[matId * 4 + 0],
        model.mat_rgba[matId * 4 + 1],
        model.mat_rgba[matId * 4 + 2],
        model.mat_rgba[matId * 4 + 3]
      ];

      // Check for texture
      const mjNTEXROLE = 10;
      const texId = model.mat_texid[matId * mjNTEXROLE + 1]; // mjTEXROLE_RGB = 1
      if (texId !== -1) {
        const width = model.tex_width[texId];
        const height = model.tex_height[texId];
        const offset = model.tex_adr[texId];
        const channels = model.tex_nchannel[texId];
        const texData = model.tex_data;
        const rgbaArray = new Uint8Array(width * height * 4);
        for (let p = 0; p < width * height; p++) {
          rgbaArray[p * 4 + 0] = texData[offset + p * channels + 0];
          rgbaArray[p * 4 + 1] = channels > 1 ? texData[offset + p * channels + 1] : rgbaArray[p * 4];
          rgbaArray[p * 4 + 2] = channels > 2 ? texData[offset + p * channels + 2] : rgbaArray[p * 4];
          rgbaArray[p * 4 + 3] = 255;
        }
        texture = new THREE.DataTexture(rgbaArray, width, height, THREE.RGBAFormat, THREE.UnsignedByteType);
        texture.repeat.set(
          model.mat_texrepeat[matId * 2 + 0] || 1,
          model.mat_texrepeat[matId * 2 + 1] || 1
        );
        texture.wrapS = THREE.RepeatWrapping;
        texture.wrapT = THREE.RepeatWrapping;
        texture.needsUpdate = true;
      }
    }

    const matOpts = {
      color: new THREE.Color(matColor[0], matColor[1], matColor[2]),
      transparent: matColor[3] < 1.0,
      opacity: matColor[3],
      roughness: 0.6,
      metalness: 0.1
    };
    if (texture) matOpts.map = texture;
    const material = new THREE.MeshStandardMaterial(matOpts);

    let mesh;
    if (type === 0) {
      mesh = new THREE.Mesh(geometry, new THREE.MeshStandardMaterial({
        color: 0x2a2a30, roughness: 0.95, metalness: 0.0, ...(texture ? {map: texture} : {})
      }));
      mesh.rotateX(-Math.PI / 2);
    } else {
      mesh = new THREE.Mesh(geometry, material);
    }

    mesh.castShadow = type !== 0;
    mesh.receiveShadow = true;

    // Set geom local transform with swizzle
    getPosition(model.geom_pos, g, mesh.position);
    if (type !== 0) getQuaternion(model.geom_quat, g, mesh.quaternion);

    bodies[b].add(mesh);
  }

  return bodies;
}

// ============================================================
// Main viewer class
// ============================================================

class G1PolicyViewer {
  constructor() {
    this.mujoco = null;  // The WASM module
    this.model = null;
    this.data = null;
    this.policySession = null;
    this.motionData = null;
    this.motionFps = 60;
    this.nFrames = 0;
    this.anchorBodyIdx = -1;
    this.lastAction = new Float32Array(N_JOINTS);
    this.simTime = 0;
    this.paused = false;
    this.bodies = {};    // Three.js body groups, keyed by body ID
    this.scene = null;
    this.camera = null;
    this.renderer = null;
    this.controls = null;
    this.fpsCounter = { frames: 0, lastTime: performance.now(), value: 0 };
  }

  async init(clipId, category, embed = false) {
    this.embed = embed;
    const status = document.getElementById('load-status');
    const progress = document.getElementById('progress-fill');
    const errorMsg = document.getElementById('error-msg');

    const notifyParent = (msg) => {
      if (window.parent !== window) {
        window.parent.postMessage({ type: 'viewer-status', clipId, status: msg }, '*');
      }
    };

    try {
      status.textContent = 'Loading MuJoCo WASM...';
      notifyParent('Loading WASM...');
      progress.style.width = '10%';
      const mjModule = await import('https://cdn.jsdelivr.net/npm/mujoco-js@0.0.7/+esm');
      this.mujoco = await mjModule.default();

      status.textContent = 'Loading G1 robot model...';
      notifyParent('Loading robot model...');
      progress.style.width = '30%';
      await this.loadModel();

      status.textContent = 'Loading neural network policy...';
      notifyParent('Loading policy...');
      progress.style.width = '50%';
      await this.loadPolicy(`${category}/${clipId}/policy/${clipId}_policy.onnx`);

      status.textContent = 'Loading reference motion...';
      notifyParent('Loading motion...');
      progress.style.width = '70%';
      await this.loadMotion(`${category}/${clipId}/training/${clipId}.npz`);

      status.textContent = 'Building 3D scene...';
      notifyParent('Building scene...');
      progress.style.width = '85%';
      this.buildRenderer();
      this.bodies = buildSceneFromModel(this.mujoco, this.model, this.data);

      // Add body groups to scene
      for (const b of Object.values(this.bodies)) {
        this.scene.add(b);
      }

      // Anchor body: torso_link = MuJoCo body 16 (0=world, 1=pelvis, ..., 16=torso)
      this.anchorBodyIdx = MUJOCO_ANCHOR_BODY;

      this.resetSimulation();
      this.resetCamera();
      this.syncBodies();

      progress.style.width = '100%';
      status.textContent = 'Ready!';

      if (!embed) {
        document.getElementById('clip-name').textContent =
          clipId.replace(/^[BJMV]_/, '').replace(/([a-z])([A-Z])/g, '$1 $2');
        document.getElementById('hud').style.display = 'flex';
        document.getElementById('controls').style.display = 'flex';
        document.getElementById('info-panel').style.display = 'block';
        this.setupControls();
      }

      setTimeout(() => document.getElementById('overlay').classList.add('hidden'), 300);
      // Notify parent frame that viewer is fully loaded and rendering
      if (window.parent !== window) {
        window.parent.postMessage({ type: 'viewer-ready', clipId }, '*');
      }
      this.animate();

    } catch (err) {
      console.error('Viewer init failed:', err);
      errorMsg.textContent = `Error: ${err.message}`;
      errorMsg.style.display = 'block';
      status.textContent = 'Failed to load';
    }
  }

  async loadModel() {
    const mj = this.mujoco;

    mj.FS.mkdir('/model');
    mj.FS.mkdir('/model/meshes');

    const xmlText = await fetch('model/g1_viewer.xml').then(r => r.text());
    mj.FS.writeFile('/model/g1_viewer.xml', xmlText);

    // Parse XML to find mesh files, fetch all in parallel
    const parser = new DOMParser();
    const doc = parser.parseFromString(xmlText, 'text/xml');
    const meshFiles = Array.from(doc.querySelectorAll('mesh[file]')).map(m => m.getAttribute('file'));

    await Promise.all(meshFiles.map(async (filename) => {
      const resp = await fetch(`model/meshes/${filename}`);
      if (!resp.ok) throw new Error(`Missing mesh: ${filename}`);
      const data = new Uint8Array(await resp.arrayBuffer());
      mj.FS.writeFile(`/model/meshes/${filename}`, data);
    }));

    this.model = mj.MjModel.loadFromXML('/model/g1_viewer.xml');
    this.data = new mj.MjData(this.model);
  }

  async loadPolicy(url) {
    this.policySession = await ort.InferenceSession.create(url, {
      executionProviders: ['wasm']
    });
  }

  async loadMotion(url) {
    const arrays = await loadNPZ(url);
    this.motionData = {
      jointPos: arrays.joint_pos,
      jointVel: arrays.joint_vel,
      bodyPosW: arrays.body_pos_w,
      bodyQuatW: arrays.body_quat_w
    };
    this.nFrames = this.motionData.jointPos.shape[0];
    if (arrays.fps) {
      const f = Number(arrays.fps.data[0]);
      if (f > 0 && f < 1000) this.motionFps = f;
    }
  }

  buildRenderer() {
    const canvas = document.getElementById('viewer-canvas');
    this.renderer = new THREE.WebGLRenderer({ canvas, antialias: !this.embed });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(this.embed ? 1 : Math.min(window.devicePixelRatio, 2));
    this.renderer.shadowMap.enabled = !this.embed;
    if (!this.embed) this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;

    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0x07070b);
    this.scene.fog = new THREE.Fog(0x07070b, 8, 25);

    this.scene.add(new THREE.AmbientLight(0xffffff, 1.0));
    const dir1 = new THREE.DirectionalLight(0xffffff, 1.5);
    dir1.position.set(3, 5, 3);
    dir1.castShadow = true;
    dir1.shadow.mapSize.set(2048, 2048);
    const sc = dir1.shadow.camera;
    sc.near = 0.5; sc.far = 20; sc.left = sc.bottom = -5; sc.right = sc.top = 5;
    this.scene.add(dir1);
    this.scene.add(new THREE.DirectionalLight(0xffffff, 0.8).translateX(-2).translateY(3));

    this.camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 100);
    this.resetCamera();

    this.controls = new OrbitControls(this.camera, canvas);
    this.controls.target.set(0, 0.8, 0); // overridden by resetCamera() after sim init
    this.controls.enableDamping = true;
    this.controls.dampingFactor = 0.05;
    this.controls.minDistance = 0.5;
    this.controls.maxDistance = 10;
    if (this.embed) {
      this.controls.autoRotate = true;
      this.controls.autoRotateSpeed = 1.5;
      this.controls.enableZoom = false;
      this.controls.enablePan = false;
    }
    this.controls.update();

    window.addEventListener('resize', () => {
      this.camera.aspect = window.innerWidth / window.innerHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(window.innerWidth, window.innerHeight);
    });
  }

  resetCamera() {
    // Compute camera position in front of robot based on its facing direction
    const dist = this.embed ? 2.1 : 2.8;
    const height = this.embed ? 1.0 : 1.2;
    let cx = 0, cy = height, cz = dist; // default: in front along +Z (Three.js)
    let tx = 0, ty = 0.8, tz = 0;

    if (this.data) {
      // Robot pelvis position (MuJoCo Z-up → Three.js Y-up)
      const px = this.data.qpos[0];
      const pz_mj = this.data.qpos[2]; // MuJoCo Z → Three.js Y
      const py_mj = this.data.qpos[1]; // MuJoCo Y → Three.js -Z

      tx = px; ty = pz_mj * 0.9; tz = -py_mj;

      // Extract robot forward direction from pelvis quaternion (MuJoCo wxyz)
      // Robot forward is +X in MuJoCo body frame
      const qw = this.data.qpos[3], qx = this.data.qpos[4];
      const qy = this.data.qpos[5], qz = this.data.qpos[6];
      // Rotate [1,0,0] by quaternion: forward in MuJoCo world frame
      const fwdX = 1 - 2*(qy*qy + qz*qz);
      const fwdY = 2*(qx*qy + qw*qz);
      // Map MuJoCo (fwdX, fwdY) → Three.js (fwdX, -fwdY) on the XZ plane
      cx = tx + fwdX * dist;
      cz = tz + (-fwdY) * dist;
      cy = ty + height;
    }

    this.camera.position.set(cx, cy, cz);
    this.camera.lookAt(tx, ty, tz);
    if (this.controls) {
      this.controls.target.set(tx, ty, tz);
      this.controls.update();
    }
  }

  resetSimulation() {
    // Reset data
    this.mujoco.mj_resetData(this.model, this.data);

    // Initialize from motion frame 0 pose (matches training initialization)
    if (this.motionData) {
      const md = this.motionData;
      const nBod = md.bodyPosW.shape[1];

      // Root position from motion frame 0, pelvis = body 0
      this.data.qpos[0] = Number(md.bodyPosW.data[0 * nBod * 3 + 0 * 3 + 0]);
      this.data.qpos[1] = Number(md.bodyPosW.data[0 * nBod * 3 + 0 * 3 + 1]);
      this.data.qpos[2] = Number(md.bodyPosW.data[0 * nBod * 3 + 0 * 3 + 2]);

      // Root quaternion from motion frame 0, pelvis = body 0 (w,x,y,z)
      this.data.qpos[3] = Number(md.bodyQuatW.data[0 * nBod * 4 + 0 * 4 + 0]);
      this.data.qpos[4] = Number(md.bodyQuatW.data[0 * nBod * 4 + 0 * 4 + 1]);
      this.data.qpos[5] = Number(md.bodyQuatW.data[0 * nBod * 4 + 0 * 4 + 2]);
      this.data.qpos[6] = Number(md.bodyQuatW.data[0 * nBod * 4 + 0 * 4 + 3]);

      // Joint positions from motion frame 0
      const jpCols = md.jointPos.shape[1] || N_JOINTS;
      for (let i = 0; i < N_JOINTS; i++) {
        this.data.qpos[7 + i] = Number(md.jointPos.data[0 * jpCols + i]);
        this.data.ctrl[i] = Number(md.jointPos.data[0 * jpCols + i]);
      }
    } else {
      // Fallback to default keyframe if no motion data loaded yet
      this.data.qpos[0] = 0; this.data.qpos[1] = 0; this.data.qpos[2] = 0.76;
      this.data.qpos[3] = 1; this.data.qpos[4] = 0; this.data.qpos[5] = 0; this.data.qpos[6] = 0;
      for (let i = 0; i < N_JOINTS; i++) {
        this.data.qpos[7 + i] = DEFAULT_JOINT_POS[i];
        this.data.ctrl[i] = DEFAULT_JOINT_POS[i];
      }
    }

    this.mujoco.mj_forward(this.model, this.data);
    this.simTime = 0;
    this.lastAction.fill(0);
  }

  getCurrentFrame() {
    return Math.floor(this.simTime * this.motionFps) % this.nFrames;
  }

  constructObservation() {
    const obs = new Float32Array(OBS_DIM);
    const frame = this.getCurrentFrame();
    const md = this.motionData;
    let idx = 0;

    // Command: ref joint_pos (29) + joint_vel (29) = 58
    const jpCols = md.jointPos.shape[1] || N_JOINTS;
    const jvCols = md.jointVel.shape[1] || N_JOINTS;
    for (let i = 0; i < N_JOINTS; i++) obs[idx++] = Number(md.jointPos.data[frame * jpCols + i]);
    for (let i = 0; i < N_JOINTS; i++) obs[idx++] = Number(md.jointVel.data[frame * jvCols + i]);

    // Motion anchor pos in body frame (3)
    const nBod = md.bodyPosW.shape[1];
    const rpOff = frame * nBod * 3 + MOTION_ANCHOR_IDX * 3;
    const refPos = [Number(md.bodyPosW.data[rpOff]), Number(md.bodyPosW.data[rpOff+1]), Number(md.bodyPosW.data[rpOff+2])];

    const ab = this.anchorBodyIdx;
    const robPos = [this.data.xpos[ab*3], this.data.xpos[ab*3+1], this.data.xpos[ab*3+2]];
    const robQuat = [this.data.xquat[ab*4], this.data.xquat[ab*4+1], this.data.xquat[ab*4+2], this.data.xquat[ab*4+3]]; // wxyz

    const dp = [refPos[0]-robPos[0], refPos[1]-robPos[1], refPos[2]-robPos[2]];
    const posB = quatRotateInv(robQuat, dp);
    obs[idx++] = posB[0]; obs[idx++] = posB[1]; obs[idx++] = posB[2];

    // Motion anchor ori in body frame (6) — first 2 columns of rotation matrix
    const rqOff = frame * nBod * 4 + MOTION_ANCHOR_IDX * 4;
    const refQuat = [
      Number(md.bodyQuatW.data[rqOff]), Number(md.bodyQuatW.data[rqOff+1]),
      Number(md.bodyQuatW.data[rqOff+2]), Number(md.bodyQuatW.data[rqOff+3])
    ];
    const oriQ = quatMul(quatInv(robQuat), refQuat);
    // Convert quaternion to rotation matrix, take first 2 columns (6 values)
    const mat = quatToMat(oriQ);
    obs[idx++] = mat[0]; obs[idx++] = mat[1]; obs[idx++] = mat[2]; // col 0
    obs[idx++] = mat[3]; obs[idx++] = mat[4]; obs[idx++] = mat[5]; // col 1

    // Base linear velocity in body frame (3) — matches velocimeter at imu_in_pelvis
    // Velocimeter = R^T * v_world + omega_body × r_imu
    const rootQuat = [this.data.qpos[3], this.data.qpos[4], this.data.qpos[5], this.data.qpos[6]];
    const linVelW = [this.data.qvel[0], this.data.qvel[1], this.data.qvel[2]];
    const linVelB = quatRotateInv(rootQuat, linVelW);
    // IMU offset in pelvis frame: (0.04525, 0, -0.08339)
    const wx = this.data.qvel[3], wy = this.data.qvel[4], wz = this.data.qvel[5];
    const rx = 0.04525, ry = 0, rz = -0.08339;
    obs[idx++] = linVelB[0] + (wy * rz - wz * ry);
    obs[idx++] = linVelB[1] + (wz * rx - wx * rz);
    obs[idx++] = linVelB[2] + (wx * ry - wy * rx);

    // Base angular velocity (3) — MuJoCo free joint qvel[3:6] is already in body frame (matches gyro)
    obs[idx++] = wx; obs[idx++] = wy; obs[idx++] = wz;

    // Joint positions relative to defaults (29)
    for (let i = 0; i < N_JOINTS; i++) obs[idx++] = this.data.qpos[7 + i] - DEFAULT_JOINT_POS[i];

    // Joint velocities (29)
    for (let i = 0; i < N_JOINTS; i++) obs[idx++] = this.data.qvel[6 + i];

    // Last actions (29)
    for (let i = 0; i < N_JOINTS; i++) obs[idx++] = this.lastAction[i];

    return obs;
  }

  async step() {
    if (this.paused) return;

    const obs = this.constructObservation();

    const inputName = this.policySession.inputNames[0];
    const outputName = this.policySession.outputNames[0];
    const tensor = new ort.Tensor('float32', obs, [1, OBS_DIM]);
    const results = await this.policySession.run({ [inputName]: tensor });
    const actions = results[outputName].data;

    // Apply: ctrl = default_pos + action * scale
    for (let i = 0; i < N_JOINTS; i++) {
      const a = Math.max(-10, Math.min(10, actions[i]));
      this.data.ctrl[i] = DEFAULT_JOINT_POS[i] + a * ACTION_SCALES[i];
      this.lastAction[i] = a;
    }

    // Step physics: 4 substeps at 0.005s = 0.02s per policy step (matching training)
    const substeps = 4;
    for (let s = 0; s < substeps; s++) {
      this.mujoco.mj_step(this.model, this.data);
    }
    this.simTime += CONTROL_DT;
  }

  syncBodies() {
    for (let b = 0; b < this.model.nbody; b++) {
      if (!(b in this.bodies)) continue;
      getPosition(this.data.xpos, b, this.bodies[b].position);
      getQuaternion(this.data.xquat, b, this.bodies[b].quaternion);
    }
  }

  animate() {
    const loop = async () => {
      requestAnimationFrame(loop);

      try { await this.step(); } catch (e) { console.error('Step:', e); }

      this.syncBodies();

      // Track robot pelvis (body 1) with camera
      if (this.bodies[1]) {
        const p = this.bodies[1].position;
        this.controls.target.lerp(new THREE.Vector3(p.x, p.y, p.z), 0.05);
      }

      this.controls.update();
      this.renderer.render(this.scene, this.camera);

      // FPS
      this.fpsCounter.frames++;
      const now = performance.now();
      if (now - this.fpsCounter.lastTime > 1000) {
        this.fpsCounter.value = Math.round(this.fpsCounter.frames * 1000 / (now - this.fpsCounter.lastTime));
        this.fpsCounter.frames = 0;
        this.fpsCounter.lastTime = now;
        document.getElementById('info-fps').textContent = `${this.fpsCounter.value} FPS`;
      }
      document.getElementById('info-frame').textContent =
        `Frame: ${this.getCurrentFrame()} / ${this.nFrames}`;
    };
    loop();
  }

  setupControls() {
    const pauseBtn = document.getElementById('btn-pause');
    const resetBtn = document.getElementById('btn-reset');
    const cameraBtn = document.getElementById('btn-camera');

    pauseBtn.addEventListener('click', () => {
      this.paused = !this.paused;
      pauseBtn.textContent = this.paused ? 'Play' : 'Pause';
      pauseBtn.classList.toggle('active', this.paused);
    });

    resetBtn.addEventListener('click', () => {
      this.resetSimulation();
      this.syncBodies();
    });

    cameraBtn.addEventListener('click', () => {
      this.resetCamera();
      this.controls.target.set(0, 0.8, 0);
      this.controls.update();
    });

    document.addEventListener('keydown', (e) => {
      if (e.code === 'Space') { e.preventDefault(); pauseBtn.click(); }
    });
  }
}

// ============================================================
// Entry point
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  const params = new URLSearchParams(window.location.search);
  const clip = params.get('clip');
  const category = params.get('category');
  const embed = params.get('embed') === '1';

  if (!clip || !category) {
    document.getElementById('load-status').textContent = 'Missing clip or category parameter';
    return;
  }

  new G1PolicyViewer().init(clip, category, embed);
});
