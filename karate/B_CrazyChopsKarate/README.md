# B_CrazyChopsKarate

**Category:** Karate | **Performer:** Mitch Chaiet | **Duration:** 24.2s | **Frames:** 1452

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.95 rad/s |
| Joint velocity (max) | 24.28 rad/s |
| Root displacement | 11.98 m |
| Root velocity (mean) | 0.50 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1452, 3), `root_rot` (1452, 4), `dof_pos` (1452, 29)
- **NPZ**: Training data — `joint_pos/vel` (1451, 29), `body_pos/quat/vel` (1451, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
