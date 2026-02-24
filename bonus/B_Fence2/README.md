# B_Fence2

**Category:** Bonus | **Performer:** Mitch Chaiet | **Duration:** 10.63s | **Frames:** 638

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.62 rad/s |
| Joint velocity (max) | 52.09 rad/s |
| Root displacement | 4.78 m |
| Root velocity (mean) | 0.45 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (638, 3), `root_rot` (638, 4), `dof_pos` (638, 29)
- **NPZ**: Training data — `joint_pos/vel` (637, 29), `body_pos/quat/vel` (637, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
