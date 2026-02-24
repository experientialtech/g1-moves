# B_HandsChop

**Category:** Bonus | **Performer:** Mitch Chaiet | **Duration:** 29.43s | **Frames:** 1766

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.34 rad/s |
| Joint velocity (max) | 13.70 rad/s |
| Root displacement | 1.07 m |
| Root velocity (mean) | 0.04 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1766, 3), `root_rot` (1766, 4), `dof_pos` (1766, 29)
- **NPZ**: Training data — `joint_pos/vel` (1765, 29), `body_pos/quat/vel` (1765, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
