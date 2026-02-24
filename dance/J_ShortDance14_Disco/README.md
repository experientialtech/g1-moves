# J_ShortDance14_Disco

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 14.3s | **Frames:** 858

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.87 rad/s |
| Joint velocity (max) | 44.21 rad/s |
| Root displacement | 2.73 m |
| Root velocity (mean) | 0.19 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (858, 3), `root_rot` (858, 4), `dof_pos` (858, 29)
- **NPZ**: Training data — `joint_pos/vel` (857, 29), `body_pos/quat/vel` (857, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
