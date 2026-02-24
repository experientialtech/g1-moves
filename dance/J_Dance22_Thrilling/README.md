# J_Dance22_Thrilling

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 26.98s | **Frames:** 1619

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.60 rad/s |
| Joint velocity (max) | 53.36 rad/s |
| Root displacement | 5.48 m |
| Root velocity (mean) | 0.20 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1619, 3), `root_rot` (1619, 4), `dof_pos` (1619, 29)
- **NPZ**: Training data — `joint_pos/vel` (1618, 29), `body_pos/quat/vel` (1618, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
