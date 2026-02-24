# J_Dance1_Modern

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 37.75s | **Frames:** 2265

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.28 rad/s |
| Joint velocity (max) | 45.27 rad/s |
| Root displacement | 4.25 m |
| Root velocity (mean) | 0.11 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2265, 3), `root_rot` (2265, 4), `dof_pos` (2265, 29)
- **NPZ**: Training data — `joint_pos/vel` (2264, 29), `body_pos/quat/vel` (2264, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
