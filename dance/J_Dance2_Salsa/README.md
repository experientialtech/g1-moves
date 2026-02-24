# J_Dance2_Salsa

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 35.85s | **Frames:** 2151

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.69 rad/s |
| Joint velocity (max) | 79.60 rad/s |
| Root displacement | 8.45 m |
| Root velocity (mean) | 0.24 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2151, 3), `root_rot` (2151, 4), `dof_pos` (2151, 29)
- **NPZ**: Training data — `joint_pos/vel` (2150, 29), `body_pos/quat/vel` (2150, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
