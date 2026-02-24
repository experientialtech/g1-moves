# M_Move1

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 31.17s | **Frames:** 1870

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.50 rad/s |
| Joint velocity (max) | 27.86 rad/s |
| Root displacement | 7.45 m |
| Root velocity (mean) | 0.24 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1870, 3), `root_rot` (1870, 4), `dof_pos` (1870, 29)
- **NPZ**: Training data — `joint_pos/vel` (1869, 29), `body_pos/quat/vel` (1869, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
