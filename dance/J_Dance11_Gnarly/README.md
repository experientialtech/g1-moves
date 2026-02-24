# J_Dance11_Gnarly

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 45.15s | **Frames:** 2709

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
| Joint velocity (max) | 51.85 rad/s |
| Root displacement | 8.58 m |
| Root velocity (mean) | 0.19 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2709, 3), `root_rot` (2709, 4), `dof_pos` (2709, 29)
- **NPZ**: Training data — `joint_pos/vel` (2708, 29), `body_pos/quat/vel` (2708, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
