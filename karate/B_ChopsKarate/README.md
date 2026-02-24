# B_ChopsKarate

**Category:** Karate | **Performer:** Mitch Chaiet | **Duration:** 52.67s | **Frames:** 3160

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.78 rad/s |
| Joint velocity (max) | 39.13 rad/s |
| Root displacement | 29.92 m |
| Root velocity (mean) | 0.57 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (3160, 3), `root_rot` (3160, 4), `dof_pos` (3160, 29)
- **NPZ**: Training data — `joint_pos/vel` (3159, 29), `body_pos/quat/vel` (3159, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
