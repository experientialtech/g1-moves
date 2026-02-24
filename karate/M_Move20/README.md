# M_Move20

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 23.57s | **Frames:** 1414

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.46 rad/s |
| Joint velocity (max) | 11.45 rad/s |
| Root displacement | 4.95 m |
| Root velocity (mean) | 0.21 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1414, 3), `root_rot` (1414, 4), `dof_pos` (1414, 29)
- **NPZ**: Training data — `joint_pos/vel` (1413, 29), `body_pos/quat/vel` (1413, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
