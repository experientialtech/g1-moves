# B_SpiralDance

**Category:** Dance | **Performer:** Mitch Chaiet | **Duration:** 47.8s | **Frames:** 2868

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.51 rad/s |
| Joint velocity (max) | 56.12 rad/s |
| Root displacement | 5.31 m |
| Root velocity (mean) | 0.11 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2868, 3), `root_rot` (2868, 4), `dof_pos` (2868, 29)
- **NPZ**: Training data — `joint_pos/vel` (2867, 29), `body_pos/quat/vel` (2867, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
