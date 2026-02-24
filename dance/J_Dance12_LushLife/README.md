# J_Dance12_LushLife

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 35.6s | **Frames:** 2136

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.88 rad/s |
| Joint velocity (max) | 68.49 rad/s |
| Root displacement | 8.29 m |
| Root velocity (mean) | 0.23 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2136, 3), `root_rot` (2136, 4), `dof_pos` (2136, 29)
- **NPZ**: Training data — `joint_pos/vel` (2135, 29), `body_pos/quat/vel` (2135, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
