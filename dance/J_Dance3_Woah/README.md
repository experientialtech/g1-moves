# J_Dance3_Woah

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 30.0s | **Frames:** 1800

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.57 rad/s |
| Joint velocity (max) | 68.68 rad/s |
| Root displacement | 5.57 m |
| Root velocity (mean) | 0.19 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1800, 3), `root_rot` (1800, 4), `dof_pos` (1800, 29)
- **NPZ**: Training data — `joint_pos/vel` (1799, 29), `body_pos/quat/vel` (1799, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
