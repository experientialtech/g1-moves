# J_Dance17_Shuffle

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 32.03s | **Frames:** 1922

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 1.07 rad/s |
| Joint velocity (max) | 26.58 rad/s |
| Root displacement | 12.94 m |
| Root velocity (mean) | 0.40 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1922, 3), `root_rot` (1922, 4), `dof_pos` (1922, 29)
- **NPZ**: Training data — `joint_pos/vel` (1921, 29), `body_pos/quat/vel` (1921, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
