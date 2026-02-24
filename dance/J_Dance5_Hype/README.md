# J_Dance5_Hype

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 31.6s | **Frames:** 1896

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 1.23 rad/s |
| Joint velocity (max) | 103.60 rad/s |
| Root displacement | 13.44 m |
| Root velocity (mean) | 0.43 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1896, 3), `root_rot` (1896, 4), `dof_pos` (1896, 29)
- **NPZ**: Training data — `joint_pos/vel` (1895, 29), `body_pos/quat/vel` (1895, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
