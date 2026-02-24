# M_Move7

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 23.82s | **Frames:** 1429

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.99 rad/s |
| Joint velocity (max) | 27.30 rad/s |
| Root displacement | 9.13 m |
| Root velocity (mean) | 0.38 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1429, 3), `root_rot` (1429, 4), `dof_pos` (1429, 29)
- **NPZ**: Training data — `joint_pos/vel` (1428, 29), `body_pos/quat/vel` (1428, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
