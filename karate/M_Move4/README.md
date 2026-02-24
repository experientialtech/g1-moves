# M_Move4

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 29.25s | **Frames:** 1755

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.73 rad/s |
| Joint velocity (max) | 92.75 rad/s |
| Root displacement | 8.86 m |
| Root velocity (mean) | 0.30 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1755, 3), `root_rot` (1755, 4), `dof_pos` (1755, 29)
- **NPZ**: Training data — `joint_pos/vel` (1754, 29), `body_pos/quat/vel` (1754, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
