# J_Dance6_Sassy

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 31.9s | **Frames:** 1914

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.53 rad/s |
| Joint velocity (max) | 84.94 rad/s |
| Root displacement | 6.94 m |
| Root velocity (mean) | 0.22 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1914, 3), `root_rot` (1914, 4), `dof_pos` (1914, 29)
- **NPZ**: Training data — `joint_pos/vel` (1913, 29), `body_pos/quat/vel` (1913, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
