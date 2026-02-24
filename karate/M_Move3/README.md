# M_Move3

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 31.97s | **Frames:** 1918

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.59 rad/s |
| Joint velocity (max) | 21.87 rad/s |
| Root displacement | 7.45 m |
| Root velocity (mean) | 0.23 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1918, 3), `root_rot` (1918, 4), `dof_pos` (1918, 29)
- **NPZ**: Training data — `joint_pos/vel` (1917, 29), `body_pos/quat/vel` (1917, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
