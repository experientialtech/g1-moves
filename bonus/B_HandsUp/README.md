# B_HandsUp

**Category:** Bonus | **Performer:** Mitch Chaiet | **Duration:** 7.37s | **Frames:** 442

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.33 rad/s |
| Joint velocity (max) | 10.17 rad/s |
| Root displacement | 0.23 m |
| Root velocity (mean) | 0.03 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (442, 3), `root_rot` (442, 4), `dof_pos` (442, 29)
- **NPZ**: Training data — `joint_pos/vel` (441, 29), `body_pos/quat/vel` (441, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
