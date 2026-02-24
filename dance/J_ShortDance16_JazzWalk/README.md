# J_ShortDance16_JazzWalk

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 10.62s | **Frames:** 637

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.97 rad/s |
| Joint velocity (max) | 14.57 rad/s |
| Root displacement | 4.23 m |
| Root velocity (mean) | 0.40 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (637, 3), `root_rot` (637, 4), `dof_pos` (637, 29)
- **NPZ**: Training data — `joint_pos/vel` (636, 29), `body_pos/quat/vel` (636, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
