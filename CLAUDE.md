# G1 Moves — Motion-to-Policy Pipeline

## Project Overview

This repository contains 59 motion capture clips for the Unitree G1 humanoid robot (mode 15, 29 DOF). The pipeline takes raw BVH motion capture from MOVIN3D and processes it through retargeting, training data generation, RL policy training, and archival.

**Robot**: Unitree G1, mode 15, 29 DOF
**Capture systems**: MOVIN TRACIN (markerless, LiDAR + vision), video2robot (monocular video)
**Training framework**: mjlab (MuJoCo-Warp + RSL-RL PPO)
**Workstation**: Dell Pro Max Tower T2, RTX PRO 6000 (96GB), Ubuntu 24.04

## Repository Layout

```
g1-moves/
  dance/                        28 clips
  karate/                       27 clips
  bonus/                         4 clips
  <category>/<clip>/
    capture/                    Original mocap
      <clip>.bvh                BVH motion (51-joint humanoid, 60 FPS)
      <clip>.gif                Preview GIF
      <clip>.mp4                Preview video
      <clip>_{bl,mb,ue,un}.fbx  FBX exports
    retarget/                   G1 retargeting
      <clip>.pkl                Retargeted joints (29 DOF)
      <clip>.csv                Same as PKL in CSV format
      <clip>_retarget.gif       Retarget preview
      <clip>_retarget.mp4       Retarget video
    training/                   RL training data
      <clip>.npz                Training-ready data
      <clip>_training.gif       Training visualization
      <clip>_training.mp4       Training video
    policy/                     Trained RL policy (when available)
      <clip>_policy.pt          PyTorch checkpoint
      <clip>_policy.gif         Policy rollout GIF
      <clip>_policy.mp4         Policy rollout video
      agent.yaml                PPO hyperparameters
      env.yaml                  Full environment config
      training_log.csv          Training metrics
  external/
    video2robot/                video2robot pipeline (monocular video → robot motion)
  manifest.json                 Per-clip metadata index
  quality_report.json           Automated validation
  generate_metadata.py          Regenerate metadata
  retarget_all.py               Batch retarget pipeline
  DATASET_CARD.md               Dataset documentation
```

## Key Paths

| What | Path |
|------|------|
| This repo | `~/Repositories/g1-moves` |
| mjlab-gui | `~/Repositories/mjlab-gui` |
| G1 URDF | `~/Repositories/g1-urdf` |
| MuJoCo XML | `~/Repositories/g1-urdf/g1_mode15_square.xml` |
| Training logs | `~/Repositories/mjlab-gui/logs/rsl_rl/g1_tracking/` |
| video2robot | `~/Repositories/g1-moves/external/video2robot` |
| GMR | `~/Repositories/g1-moves/external/video2robot/third_party/GMR` |
| PromptHMR | `~/Repositories/g1-moves/external/video2robot/third_party/PromptHMR` |

## Pipeline Stages

There are two input paths that converge at the PKL stage:
- **Path A (BVH)**: MOVIN TRACIN → BVH → retarget_all.py → PKL (Stage 1)
- **Path B (Video)**: Any video → PromptHMR → SMPL-X → GMR → PKL (Stage 0)

Both produce the same PKL format and feed into Stage 2+ identically.

### Stage 0: Video to PKL via video2robot

Extracts human pose from monocular video (YouTube, phone, etc.) and retargets to G1 robot joints. Alternative to the BVH pipeline for clips without mocap hardware.

**Input**: Any MP4 video with a visible full-body human
**Output**: `<category>/<clip>/retarget/<clip>.pkl`, `<clip>.csv`

**Environments**: Two separate conda envs required (conflicting deps):
- `phmr` (Python 3.11) — PromptHMR pose extraction (PyTorch 2.9+, xformers, SAM2, detectron2)
- `gmr` (Python 3.10) — GMR motion retargeting (MuJoCo, mink IK solver)

#### Step 1: Set up project directory

```bash
CLIP=V_MyClip
CATEGORY=bonus
V2R=~/Repositories/g1-moves/external/video2robot

# Create project folder with video
mkdir -p $V2R/data/$CLIP
cp /path/to/video.mp4 $V2R/data/$CLIP/original.mp4
```

Or download from YouTube:
```bash
yt-dlp -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" \
  -o "$V2R/data/$CLIP/original.mp4" "https://youtube.com/..."
```

#### Step 2: Extract pose (PromptHMR)

```bash
cd $V2R
conda run -n phmr python scripts/extract_pose.py \
  --project data/$CLIP --static-camera
```

**What it does**:
1. Converts video to H.264 if needed (AV1, VP9, etc.)
2. Runs person detection + SAM2 tracking
3. Estimates 3D human mesh (SMPL-X) per frame via PromptHMR
4. Exports `smplx.npz` with root_orient, pose_body, betas, trans

**Output**: `data/$CLIP/smplx.npz`, `smplx_tracks.json`, `results.pkl`, `world4d.glb`

**Flags**:
- `--static-camera`: Skip SLAM camera estimation (use for tripod/fixed-camera videos)

**Time**: ~2-5 min on RTX PRO 6000

#### Step 3: Retarget to G1 (GMR)

```bash
cd $V2R
conda run -n gmr python scripts/convert_to_robot.py \
  --project data/$CLIP --robot unitree_g1 --no-twist
```

**What it does**:
1. Loads SMPL-X body model, computes human height from betas
2. Per-frame IK: maps SMPL-X joints → G1 29-DOF joint angles
3. Forward kinematics for body positions + ground calibration
4. Saves PKL: `{fps, root_pos (N,3), root_rot (N,4) xyzw, dof_pos (N,29)}`

**Output**: `data/$CLIP/robot_motion.pkl`

**Flags**:
- `--no-twist`: Skip 23-DOF TWIST conversion (we use 29-DOF)
- `--all-tracks`: Retarget every detected person (default: best track only)
- `--fps 60`: Upsample to 60 FPS (default: keep original video FPS)

**Time**: ~30s for 285 frames

#### Step 4: Copy to g1-moves and generate CSV

```bash
mkdir -p ~/Repositories/g1-moves/$CATEGORY/$CLIP/{capture,retarget,training,policy}

# Copy video + retarget output
cp $V2R/data/$CLIP/original.mp4 ~/Repositories/g1-moves/$CATEGORY/$CLIP/capture/$CLIP.mp4
cp $V2R/data/$CLIP/robot_motion.pkl ~/Repositories/g1-moves/$CATEGORY/$CLIP/retarget/$CLIP.pkl

# Generate CSV (36 columns: 3 pos + 4 quat_xyzw + 29 joints)
python3 -c "
import pickle, numpy as np
with open('$HOME/Repositories/g1-moves/$CATEGORY/$CLIP/retarget/$CLIP.pkl','rb') as f:
    d = pickle.load(f)
combined = np.hstack([d['root_pos'], d['root_rot'], d['dof_pos']])
np.savetxt('$HOME/Repositories/g1-moves/$CATEGORY/$CLIP/retarget/$CLIP.csv', combined, delimiter=',', fmt='%.10f')
print(f'CSV: {combined.shape[0]} frames x {combined.shape[1]} cols')
"
```

#### Step 5: Visualize in MuJoCo

```bash
cd ~/Repositories/g1-moves/external/video2robot/third_party/GMR
conda run -n gmr python scripts/vis_robot_motion.py \
  --robot unitree_g1 \
  --robot_motion_path ~/Repositories/g1-moves/$CATEGORY/$CLIP/retarget/$CLIP.pkl \
  --record_video \
  --video_path ~/Repositories/g1-moves/$CATEGORY/$CLIP/retarget/${CLIP}_retarget.mp4
```

#### Step 6: Self-collision correction

video2robot/GMR does not enforce self-collision avoidance during retargeting. Post-process to fix arm-into-arm, arm-into-torso, etc:

```bash
python3 -c "
import pickle, mujoco, numpy as np

CLIP='$CLIP'; CAT='$CATEGORY'
PKL=f'$HOME/Repositories/g1-moves/{CAT}/{CLIP}/retarget/{CLIP}.pkl'
CSV=f'$HOME/Repositories/g1-moves/{CAT}/{CLIP}/retarget/{CLIP}.csv'

with open(PKL,'rb') as f: d=pickle.load(f)
model=mujoco.MjModel.from_xml_path('$HOME/Repositories/g1-urdf/g1_mode15_square.xml')
data=mujoco.MjData(model)
rp,rr,dp=d['root_pos'].copy(),d['root_rot'].copy(),d['dof_pos'].copy()
n=len(rp)

def has_col(i):
    data.qpos[:3]=rp[i]; data.qpos[3:7]=[rr[i,3],rr[i,0],rr[i,1],rr[i,2]]; data.qpos[7:]=dp[i]
    mujoco.mj_forward(model,data)
    return any(model.body(model.geom_bodyid[data.contact[c].geom1]).name!='world'
               and model.body(model.geom_bodyid[data.contact[c].geom2]).name!='world'
               for c in range(data.ncon))

# Find collision ranges
ic=[i for i in range(n) if has_col(i)]
print(f'{len(ic)} collision frames')

# Interpolate arm joints (15-28) from boundary clean frames
ARM=list(range(15,29))
ranges=[]; i=0
while i<n:
    if has_col(i):
        s=i
        while i<n and has_col(i): i+=1
        ranges.append((s,i-1))
    else: i+=1

for s,e in ranges:
    cb=s-1; ca=e+1
    while cb>0 and has_col(cb): cb-=1
    while ca<n-1 and has_col(ca): ca+=1
    span=ca-cb
    for f in range(s,e+1):
        t=(f-cb)/span if span>0 else 0.5
        for j in ARM: dp[f,j]=(1-t)*dp[cb,j]+t*dp[ca,j]

# If any remain, widen to all joints
for _ in range(3):
    ic2=[i for i in range(n) if has_col(i)]
    if not ic2: break
    for s,e in ranges:
        cb=max(0,s-3); ca=min(n-1,e+3)
        while cb>0 and has_col(cb): cb-=1
        while ca<n-1 and has_col(ca): ca+=1
        span=ca-cb
        for f in range(s,e+1):
            if not has_col(f): continue
            t=(f-cb)/span if span>0 else 0.5
            dp[f]=(1-t)*dp[cb]+t*dp[ca]

final=sum(has_col(i) for i in range(n))
print(f'Remaining: {final}')

d['dof_pos']=dp.astype(np.float32)
with open(PKL,'wb') as f: pickle.dump(d,f)
np.savetxt(CSV,np.hstack([rp,rr,dp]),delimiter=',',fmt='%.10f')
print('Saved corrected PKL+CSV')
"
```

**Strategy**: For collision frames, interpolate arm joints (shoulder/elbow/wrist) between nearest clean boundary frames. Falls back to full-joint interpolation if arm-only doesn't resolve. Typically corrects <5 deg mean deviation, preserving motion character.

#### Verify

```bash
python3 -c "
import pickle, numpy as np, mujoco
with open('$HOME/Repositories/g1-moves/$CATEGORY/$CLIP/retarget/$CLIP.pkl','rb') as f:
    d = pickle.load(f)
assert d['dof_pos'].shape[1] == 29
assert d['root_rot'].shape[1] == 4
assert not np.any(np.isnan(d['dof_pos']))

# Self-collision check
model=mujoco.MjModel.from_xml_path('$HOME/Repositories/g1-urdf/g1_mode15_square.xml')
data=mujoco.MjData(model)
cols=0
for i in range(len(d['root_pos'])):
    data.qpos[:3]=d['root_pos'][i]
    data.qpos[3:7]=[d['root_rot'][i,3],d['root_rot'][i,0],d['root_rot'][i,1],d['root_rot'][i,2]]
    data.qpos[7:]=d['dof_pos'][i]
    mujoco.mj_forward(model,data)
    for c in range(data.ncon):
        b1=model.body(model.geom_bodyid[data.contact[c].geom1]).name
        b2=model.body(model.geom_bodyid[data.contact[c].geom2]).name
        if b1!='world' and b2!='world': cols+=1; break
print(f'frames={d[\"dof_pos\"].shape[0]}, fps={d[\"fps\"]}, dof={d[\"dof_pos\"].shape[1]}, self_collisions={cols}')
assert cols == 0, f'{cols} self-collision frames remain!'
"
```

**Then continue with Stage 2 (CSV → NPZ) and beyond.**

### Stage 1: Retarget BVH to PKL

Converts human motion capture to G1 robot joint trajectories using inverse kinematics.

**Input**: `<category>/<clip>/capture/<clip>.bvh`
**Output**: `<category>/<clip>/retarget/<clip>.pkl`

```bash
cd ~/Repositories/g1-moves
python retarget_all.py --workers 4
```

For a single clip:
```bash
python retarget_all.py --clips "B_Fence1"
```

**What it does**:
1. Loads BVH via `movin_sdk_python.load_bvh_file()` with `human_height=1.75`
2. Per-frame IK retargeting to G1 29-DOF joint limits
3. Ground calibration: MuJoCo FK finds min ankle Z, shifts root down
4. Renders 1080x1080 MP4 (libx264 CRF 18) + 360px 15fps GIF (capped at 20s)
5. Saves PKL: `{fps: 60, root_pos: (N,3), root_rot: (N,4) xyzw, dof_pos: (N,29)}`

**Verify**:
```bash
python -c "
import pickle
with open('<category>/<clip>/retarget/<clip>.pkl','rb') as f: d=pickle.load(f)
print(f'frames={d[\"dof_pos\"].shape[0]}, dof={d[\"dof_pos\"].shape[1]}')
assert d['dof_pos'].shape[1] == 29
"
```

**Time**: ~5s per clip, ~5 min for all 59 with 4 workers

### Stage 2: Convert PKL to NPZ Training Data

Runs MuJoCo forward kinematics to compute body positions, orientations, and velocities needed for RL training.

**Input**: `<category>/<clip>/retarget/<clip>.csv`
**Output**: `<category>/<clip>/training/<clip>.npz`

```bash
cd ~/Repositories/mjlab-gui
MUJOCO_GL=egl uv run python src/mjlab/scripts/csv_to_npz.py \
  --input-file ~/Repositories/g1-moves/<category>/<clip>/retarget/<clip>.csv \
  --output-name <clip> \
  --input-fps 60 \
  --output-fps 60 \
  --render
```

Or use the local wrapper (bypasses WandB):
```bash
cd ~/Repositories/mjlab-gui
MUJOCO_GL=egl python app/scripts/process_motion_local.py \
  --input-file ~/Repositories/g1-moves/<category>/<clip>/retarget/<clip>.csv \
  --output-name <clip> \
  --run-folder <clip>_$(date +%Y%m%d_%H%M%S) \
  --input-fps 60 \
  --output-fps 60 \
  --render
```

**What it does**:
1. Loads CSV (36 columns: 3 root pos + 4 root quat + 29 joint angles)
2. Optional interpolation to target FPS
3. MuJoCo FK: computes body positions, quaternions, linear/angular velocities
4. Saves NPZ with joint_pos, joint_vel, body_pos_w, body_quat_w, body_lin_vel_w, body_ang_vel_w

**Output location**: `app/datasets/processed/<clip>_<timestamp>/motion.npz`

Copy to g1-moves:
```bash
cp app/datasets/processed/<clip>_*/motion.npz \
   ~/Repositories/g1-moves/<category>/<clip>/training/<clip>.npz
```

**Verify**:
```bash
python -c "
import numpy as np
d = np.load('<clip>.npz')
print({k: d[k].shape for k in d.files})
assert 'joint_pos' in d.files and 'body_pos_w' in d.files
"
```

**Time**: ~10s per clip

### Stage 3: Render Training Visualization

Render the NPZ training data as a MuJoCo video to visually verify the processed motion.

**Input**: `<category>/<clip>/training/<clip>.npz`
**Output**: `<category>/<clip>/training/<clip>_training.mp4`, `<clip>_training.gif`

The render is produced by the `--render` flag in Stage 2, or can be generated separately using the MuJoCo offscreen renderer with the same camera settings as retarget_all.py.

### Stage 4: Train RL Policy

Train a PPO policy to imitate the reference motion in MuJoCo-Warp simulation.

**Input**: `<category>/<clip>/training/<clip>.npz`
**Output**: `~/Repositories/mjlab-gui/logs/rsl_rl/g1_tracking/<timestamp>_<clip>/`

```bash
cd ~/Repositories/mjlab-gui
MUJOCO_GL=egl MUJOCO_EGL_DEVICE_ID=0 uv run train \
  Mjlab-Tracking-Flat-Unitree-G1 \
  --env.commands.motion.motion-file ~/Repositories/g1-moves/<category>/<clip>/training/<clip>.npz \
  --env.scene.num-envs 4096 \
  --agent.max-iterations 30000 \
  --agent.save-interval 500 \
  --agent.run-name <clip> \
  --video --video-interval 5000
```

**Key parameters**:
- `num-envs 4096`: parallel simulation environments (reduce to 2048/1024 if OOM)
- `max-iterations 30000`: training steps (~6 hours on RTX PRO 6000)
- `save-interval 500`: checkpoint every 500 iterations
- `video-interval 5000`: record evaluation video every 5000 steps

**Output structure**:
```
logs/rsl_rl/g1_tracking/<timestamp>_<clip>/
  model_0.pt ... model_29999.pt    Checkpoints
  params/agent.yaml                PPO hyperparameters
  params/env.yaml                  Environment config (includes motion_file path)
  events.out.tfevents.*            TensorBoard log
  videos/                          Evaluation videos
```

**Monitor training**:
```bash
# TensorBoard
uv run tensorboard --logdir logs/rsl_rl/g1_tracking/ --port 6006

# Key metrics to watch:
# - Train/mean_reward: should increase steadily, plateau ~3-5
# - Train/mean_episode_length: should increase toward max (10s)
# - Episode_Termination/time_out: should approach 1.0 (fewer early terminations)
# - Metrics/motion/error_body_pos: should decrease
```

**Verify**:
```bash
# Check final checkpoint exists and has expected keys
python -c "
import torch
ckpt = torch.load('logs/rsl_rl/g1_tracking/<run>/model_29999.pt', map_location='cpu', weights_only=False)
print(f'iter={ckpt[\"iter\"]}, keys={list(ckpt.keys())}')
assert ckpt['iter'] == 29999
"
```

**Time**: ~6 hours for 30k iterations with 4096 envs on RTX PRO 6000

### Stage 5: Render Policy Rollout

Play back the trained policy and record video.

**Input**: trained checkpoint + NPZ motion file
**Output**: policy rollout MP4 + GIF

```bash
cd ~/Repositories/mjlab-gui
MUJOCO_GL=egl uv run play \
  Mjlab-Tracking-Flat-Unitree-G1 \
  --checkpoint-file logs/rsl_rl/g1_tracking/<run>/model_29999.pt \
  --motion-file ~/Repositories/g1-moves/<category>/<clip>/training/<clip>.npz \
  --num-envs 1 \
  --video --video-length 600
```

**Output**: `logs/rsl_rl/g1_tracking/<run>/videos/play/rl-video-step-0.mp4`

Generate GIF:
```bash
ffmpeg -y -i input.mp4 \
  -vf "fps=15,scale=360:-1:flags=lanczos,palettegen" -t 20 /tmp/palette.png
ffmpeg -y -i input.mp4 -i /tmp/palette.png \
  -t 20 -lavfi "fps=15,scale=360:-1:flags=lanczos [x]; [x][1:v] paletteuse" output.gif
```

### Stage 6: Archive to g1-moves

Copy all policy artifacts back to the clip's directory structure.

```bash
CLIP=<clip>
CATEGORY=<category>
RUN=<timestamp>_${CLIP}
LOGS=~/Repositories/mjlab-gui/logs/rsl_rl/g1_tracking/${RUN}
DEST=~/Repositories/g1-moves/${CATEGORY}/${CLIP}/policy

mkdir -p ${DEST}

# Copy final checkpoint (rename to standard name)
cp ${LOGS}/model_29999.pt ${DEST}/${CLIP}_policy.pt

# Copy training config
cp ${LOGS}/params/agent.yaml ${DEST}/agent.yaml
cp ${LOGS}/params/env.yaml ${DEST}/env.yaml

# Copy policy rollout video + generate GIF
cp ${LOGS}/videos/play/rl-video-step-0.mp4 ${DEST}/${CLIP}_policy.mp4
ffmpeg -y -i ${DEST}/${CLIP}_policy.mp4 \
  -vf "fps=15,scale=360:-1:flags=lanczos,palettegen" -t 20 /tmp/palette.png
ffmpeg -y -i ${DEST}/${CLIP}_policy.mp4 -i /tmp/palette.png \
  -t 20 -lavfi "fps=15,scale=360:-1:flags=lanczos [x]; [x][1:v] paletteuse" \
  ${DEST}/${CLIP}_policy.gif

# Extract training log from TensorBoard
python -c "
from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import csv
ea = EventAccumulator('${LOGS}')
ea.Reload()
tags = ['Train/mean_reward','Train/mean_episode_length','Loss/value_function',
        'Loss/surrogate','Loss/learning_rate','Policy/mean_noise_std',
        'Episode_Reward/motion_body_pos','Episode_Reward/motion_body_ori',
        'Episode_Reward/motion_body_lin_vel','Episode_Reward/motion_body_ang_vel',
        'Episode_Reward/motion_global_root_pos','Episode_Reward/motion_global_root_ori',
        'Episode_Reward/action_rate_l2','Episode_Reward/joint_limit',
        'Episode_Reward/self_collisions','Metrics/motion/error_anchor_pos',
        'Metrics/motion/error_anchor_rot','Metrics/motion/error_body_pos',
        'Metrics/motion/error_body_rot','Metrics/motion/error_joint_pos',
        'Episode_Termination/time_out','Episode_Termination/anchor_pos',
        'Episode_Termination/anchor_ori','Perf/total_fps']
all_data = {}
for tag in tags:
    for e in ea.Scalars(tag):
        all_data.setdefault(e.step, {})[tag.replace('/','_')] = e.value
steps = sorted(all_data)
cols = sorted(set(c for r in all_data.values() for c in r))
with open('${DEST}/training_log.csv','w',newline='') as f:
    w = csv.writer(f)
    w.writerow(['step']+cols)
    for s in steps:
        w.writerow([s]+[all_data[s].get(c,'') for c in cols])
print(f'Wrote {len(steps)} rows')
"

# Regenerate metadata
cd ~/Repositories/g1-moves
python generate_metadata.py
```

**Verify**:
```bash
ls -lh ${DEST}/
# Expected: <clip>_policy.pt, .mp4, .gif, agent.yaml, env.yaml, training_log.csv
```

### Stage 7: Commit and Push

```bash
cd ~/Repositories/g1-moves
git add ${CATEGORY}/${CLIP}/policy/ manifest.json quality_report.json ${CATEGORY}/${CLIP}/README.md
git commit -m "Add ${CLIP} trained policy with metadata"
git push
```

## Batch Processing

To process multiple clips end-to-end:

### Retarget all (Stage 1)
```bash
cd ~/Repositories/g1-moves
python retarget_all.py --workers 4
```

### Train multiple clips sequentially (Stage 4)
```bash
cd ~/Repositories/mjlab-gui
for CLIP in B_DadDance J_Dance3_Woah M_Move1; do
  CATEGORY=$(python -c "
import json
with open('$HOME/Repositories/g1-moves/manifest.json') as f:
    print(json.load(f)['clips']['${CLIP}']['category'])
  ")
  echo "=== Training ${CLIP} (${CATEGORY}) ==="
  MUJOCO_GL=egl MUJOCO_EGL_DEVICE_ID=0 uv run train \
    Mjlab-Tracking-Flat-Unitree-G1 \
    --env.commands.motion.motion-file ~/Repositories/g1-moves/${CATEGORY}/${CLIP}/training/${CLIP}.npz \
    --env.scene.num-envs 4096 \
    --agent.max-iterations 30000 \
    --agent.save-interval 500 \
    --agent.run-name ${CLIP} \
    --video --video-interval 5000
done
```

### Batch archive all new policies (Stage 6)
After training completes, archive each run:
```bash
cd ~/Repositories/mjlab-gui/logs/rsl_rl/g1_tracking/
for RUN_DIR in */; do
  CLIP=$(echo ${RUN_DIR} | sed 's/.*_//' | sed 's/\///')
  # ... run Stage 6 commands for each
done
```

## Sim-to-Real Deployment

After training a policy, deploy it to the physical G1 robot.

### Sim2Sim Validation (MuJoCo to MuJoCo)

Test the policy in a clean MuJoCo environment before deploying to hardware:

```bash
cd ~/Repositories/mjlab-gui
MUJOCO_GL=egl uv run play \
  Mjlab-Tracking-Flat-Unitree-G1 \
  --checkpoint-file logs/rsl_rl/g1_tracking/<run>/model_29999.pt \
  --motion-file ~/Repositories/g1-moves/<category>/<clip>/training/<clip>.npz \
  --num-envs 1 \
  --no-terminations \
  --viewer viser
```

Open http://localhost:8080 to view 3D visualization.

### Deploy to Physical Robot

Uses RoboJuDo framework in `~/Repositories/mjlab-gui/external/RoboJuDo/`.

**Entry point**: `python scripts/run_pipeline.py --config=<config_name>`

#### Step 1: Export policy to TorchScript JIT

mjlab saves standard PyTorch checkpoints. RoboJuDo requires TorchScript JIT (`.pt`) or ONNX (`.onnx`). Export the actor network:

```bash
cd ~/Repositories/mjlab-gui
python -c "
import torch
ckpt = torch.load('logs/rsl_rl/g1_tracking/<run>/model_29999.pt', map_location='cpu', weights_only=False)
# Extract actor network from RSL-RL checkpoint
actor = ckpt['model_state_dict']  # Adapt based on actual model architecture
# Script and save
# scripted = torch.jit.script(actor_module)
# scripted.save('exported_policy.pt')
print('Keys:', list(ckpt.keys()))
"
```

> **Note**: The exact export procedure depends on the mjlab actor architecture. You may need to instantiate the actor class from `src/mjlab/rl/` and load state dict before scripting. This step needs refinement once the first full training run completes.

#### Step 2: Create a RoboJuDo config class

Add a config to `robojudo/config/g1/g1_cfg.py` for the mjlab-trained policy. Use an existing config as template:

- **Sim validation**: Extend `g1` (uses `G1MujocoEnvCfg`)
- **Real robot**: Extend `g1_real` (uses `G1RealEnvCfg`)

Key config components:
- **Policy**: Point to exported `.pt` file, define obs/action DOF mappings
- **Environment**: `G1MujocoEnvCfg` (sim) or `G1RealEnvCfg` (real)
- **Controller**: `JoystickCtrlCfg` (sim), `UnitreeCtrlCfg` (real), or `MotionCtrlCfg` (motion playback)

#### Step 3: Network setup (real robot only)

Configure the network interface in `robojudo/config/g1/env/g1_real_env_cfg.py`:

```python
class G1RealEnvCfg(G1EnvCfg, UnitreeEnvCfg):
    unitree: UnitreeEnvCfg.UnitreeCfg = UnitreeEnvCfg.UnitreeCfg(
        net_if="eth0",           # Run `ifconfig` to find your interface
        robot="g1",
        msg_type="hg",           # G1 uses "hg" message type
        hand_type="NONE",        # No dexterous hands
        enable_odometry=True,
    )
```

Connect to G1 via Ethernet (robot at `192.168.123.10`, workstation at `192.168.123.100`).

#### Step 4: Run

```bash
cd ~/Repositories/mjlab-gui/external/RoboJuDo

# Sim2sim validation first
python scripts/run_pipeline.py --config=g1

# Real robot deployment
python scripts/run_pipeline.py --config=g1_real
```

The pipeline runs an infinite control loop at 50 Hz (`dt=0.02`). Emergency stop: press `A` button on controller or `Esc` on keyboard.

#### Available configs

| Config | Environment | Description |
|--------|------------|-------------|
| `g1` | MuJoCo sim | Default sim2sim with joystick |
| `g1_real` | Real robot | Unitree controller |
| `g1_beyondmimic` | MuJoCo sim | Motion imitation (ONNX) |
| `g1_switch` | MuJoCo sim | Multi-policy switching |
| `g1_h2h` | MuJoCo sim | Human2Humanoid motion imitation |

#### Policy format reference

| Format | Used by | Loading |
|--------|---------|---------|
| TorchScript JIT (`.pt`) | UnitreePolicy, AMOPolicy, H2HPolicy | `torch.jit.load()` |
| ONNX (`.onnx`) | BeyondMimicPolicy, ASAPPolicy | `onnxruntime.InferenceSession()` |

**Safety**: Always have the robot on a tether/harness for first deployment of new motions. During real robot initialization (~1000 steps), place the robot on the ground for sensor calibration. Start with slow, low-energy clips (B_Fence1, B_DadDance) before attempting high-energy dance or karate motions.

## Environment Setup

```bash
# Required for headless MuJoCo rendering
export MUJOCO_GL=egl
export MUJOCO_EGL_DEVICE_ID=0

# GPU selection (if multiple GPUs)
export CUDA_VISIBLE_DEVICES=0

# Python execution in mjlab-gui
cd ~/Repositories/mjlab-gui
uv run <command>       # Uses pyproject.toml dependencies

# Python execution in g1-moves
cd ~/Repositories/g1-moves
python <script>        # Uses system Python with movin_sdk_python

# video2robot (two conda envs)
conda run -n phmr python <script>   # Pose extraction (PromptHMR)
conda run -n gmr python <script>    # Motion retargeting (GMR)
```

## Common Issues

| Problem | Fix |
|---------|-----|
| `CUDA out of memory` | Reduce `--env.scene.num-envs` (4096 -> 2048 -> 1024) |
| `MUJOCO_GL error` | Set `export MUJOCO_GL=egl` before running |
| `movin_sdk_python not found` | `pip install movin_sdk_python` |
| `WandB login prompt` | Use `process_motion_local.py` wrapper instead of `csv_to_npz.py` |
| Training reward not improving | Check motion NPZ is valid, try lower learning rate (1e-4) |
| Policy falls immediately | Train longer, or check ground calibration in retarget step |
| TensorBoard empty | Run `uv run tensorboard --logdir logs/rsl_rl` from mjlab-gui dir |
| SMPL-X betas size mismatch | Pass `num_betas=10` to `smplx.create()` in GMR's `smpl.py` |
| PromptHMR sam2 warning | Non-critical `_C.so undefined symbol` — results are unaffected |
| video2robot AV1 codec | PromptHMR auto-converts to H.264; no manual step needed |

## Data Formats

| Format | Columns/Keys | Shape |
|--------|-------------|-------|
| **BVH** | 51-joint humanoid skeleton | N frames at 60 FPS |
| **PKL** | fps, root_pos, root_rot (xyzw), dof_pos | (N, 3), (N, 4), (N, 29) |
| **CSV** | root_xyz + root_quat_xyzw + 29 joints | N rows x 36 cols, no header |
| **NPZ** | fps, joint_pos, joint_vel, body_pos_w, body_quat_w, body_lin_vel_w, body_ang_vel_w | (N, 29), (N, 30, 3/4) |
| **PT** | model_state_dict, optimizer_state_dict, iter, infos | PyTorch checkpoint |
