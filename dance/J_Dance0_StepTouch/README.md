# J_Dance0_StepTouch

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 32.48s | **Frames:** 1949

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.64 rad/s |
| Joint velocity (max) | 38.77 rad/s |
| Root displacement | 5.72 m |
| Root velocity (mean) | 0.18 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1949, 3), `root_rot` (1949, 4), `dof_pos` (1949, 29)
- **NPZ**: Training data — `joint_pos/vel` (1949, 29), `body_pos/quat/vel` (1949, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
