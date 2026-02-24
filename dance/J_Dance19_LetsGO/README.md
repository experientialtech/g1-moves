# J_Dance19_LetsGO

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 24.85s | **Frames:** 1491

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
| Joint velocity (max) | 71.98 rad/s |
| Root displacement | 4.91 m |
| Root velocity (mean) | 0.20 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1491, 3), `root_rot` (1491, 4), `dof_pos` (1491, 29)
- **NPZ**: Training data — `joint_pos/vel` (1490, 29), `body_pos/quat/vel` (1490, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
