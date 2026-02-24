# B_LongKarate

**Category:** Karate | **Performer:** Mitch Chaiet | **Duration:** 48.02s | **Frames:** 2881

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
| Joint velocity (max) | 23.60 rad/s |
| Root displacement | 19.89 m |
| Root velocity (mean) | 0.41 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2881, 3), `root_rot` (2881, 4), `dof_pos` (2881, 29)
- **NPZ**: Training data — `joint_pos/vel` (2880, 29), `body_pos/quat/vel` (2880, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
