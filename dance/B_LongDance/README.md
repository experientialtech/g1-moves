# B_LongDance

**Category:** Dance | **Performer:** Mitch Chaiet | **Duration:** 119.45s | **Frames:** 7167

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 1.00 rad/s |
| Joint velocity (max) | 101.57 rad/s |
| Root displacement | 39.97 m |
| Root velocity (mean) | 0.33 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (7167, 3), `root_rot` (7167, 4), `dof_pos` (7167, 29)
- **NPZ**: Training data — `joint_pos/vel` (7166, 29), `body_pos/quat/vel` (7166, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
