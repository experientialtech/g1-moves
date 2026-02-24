# J_Dance21_Blunt

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 28.75s | **Frames:** 1725

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.56 rad/s |
| Joint velocity (max) | 36.42 rad/s |
| Root displacement | 7.49 m |
| Root velocity (mean) | 0.26 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1725, 3), `root_rot` (1725, 4), `dof_pos` (1725, 29)
- **NPZ**: Training data — `joint_pos/vel` (1724, 29), `body_pos/quat/vel` (1724, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
