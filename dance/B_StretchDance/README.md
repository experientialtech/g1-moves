# B_StretchDance

**Category:** Dance | **Performer:** Mitch Chaiet | **Duration:** 43.1s | **Frames:** 2586

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
| Joint velocity (max) | 52.71 rad/s |
| Root displacement | 3.61 m |
| Root velocity (mean) | 0.08 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2586, 3), `root_rot` (2586, 4), `dof_pos` (2586, 29)
- **NPZ**: Training data — `joint_pos/vel` (2585, 29), `body_pos/quat/vel` (2585, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
