# J_Dance8_WestCoast

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 39.92s | **Frames:** 2395

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.76 rad/s |
| Joint velocity (max) | 43.09 rad/s |
| Root displacement | 10.98 m |
| Root velocity (mean) | 0.28 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2395, 3), `root_rot` (2395, 4), `dof_pos` (2395, 29)
- **NPZ**: Training data — `joint_pos/vel` (2394, 29), `body_pos/quat/vel` (2394, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
