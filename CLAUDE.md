# G1 Moves — Motion-to-Policy Pipeline

## Project Overview

This repository contains 59 motion capture clips for the Unitree G1 humanoid robot (mode 15, 29 DOF). The pipeline takes raw BVH motion capture from MOVIN3D and processes it through retargeting, training data generation, RL policy training, and archival.

**Robot**: Unitree G1, mode 15, 29 DOF
**Capture system**: MOVIN TRACIN (markerless, LiDAR + vision)
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

## Pipeline Stages

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

Uses RoboJuDo framework in `~/Repositories/mjlab-gui/external/RoboJuDo/`:

1. **Network setup**: Connect to G1 via Ethernet
   - Robot IP: `192.168.123.10`
   - Workstation IP: `192.168.123.100`

2. **Export policy**:
   ```bash
   cd ~/Repositories/mjlab-gui/external/RoboJuDo
   python scripts/export_policy.py \
     --checkpoint ~/Repositories/mjlab-gui/logs/rsl_rl/g1_tracking/<run>/model_29999.pt
   ```

3. **Run on robot**:
   ```bash
   python scripts/deploy.py \
     --robot g1 \
     --policy exported_policy.pt \
     --motion-file ~/Repositories/g1-moves/<category>/<clip>/training/<clip>.npz
   ```

**Safety**: Always have the robot on a tether/harness for first deployment of new motions. Start with slow, low-energy clips (B_Fence1, B_DadDance) before attempting high-energy dance or karate motions.

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

## Data Formats

| Format | Columns/Keys | Shape |
|--------|-------------|-------|
| **BVH** | 51-joint humanoid skeleton | N frames at 60 FPS |
| **PKL** | fps, root_pos, root_rot (xyzw), dof_pos | (N, 3), (N, 4), (N, 29) |
| **CSV** | root_xyz + root_quat_xyzw + 29 joints | N rows x 36 cols, no header |
| **NPZ** | fps, joint_pos, joint_vel, body_pos_w, body_quat_w, body_lin_vel_w, body_ang_vel_w | (N, 29), (N, 30, 3/4) |
| **PT** | model_state_dict, optimizer_state_dict, iter, infos | PyTorch checkpoint |
