# J_Dance9_PeaceMaker

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 58.35s | **Frames:** 3501

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.72 rad/s |
| Joint velocity (max) | 105.80 rad/s |
| Root displacement | 15.20 m |
| Root velocity (mean) | 0.26 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (3501, 3), `root_rot` (3501, 4), `dof_pos` (3501, 29)
- **NPZ**: Training data — `joint_pos/vel` (3500, 29), `body_pos/quat/vel` (3500, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
