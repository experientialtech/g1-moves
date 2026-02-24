# J_Dance18_TikTok

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 17.95s | **Frames:** 1077

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 1.13 rad/s |
| Joint velocity (max) | 54.65 rad/s |
| Root displacement | 4.67 m |
| Root velocity (mean) | 0.26 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1077, 3), `root_rot` (1077, 4), `dof_pos` (1077, 29)
- **NPZ**: Training data — `joint_pos/vel` (1076, 29), `body_pos/quat/vel` (1076, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
