# M_ShortMove12

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 7.78s | **Frames:** 467

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
| Joint velocity (max) | 18.61 rad/s |
| Root displacement | 2.76 m |
| Root velocity (mean) | 0.36 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (467, 3), `root_rot` (467, 4), `dof_pos` (467, 29)
- **NPZ**: Training data — `joint_pos/vel` (466, 29), `body_pos/quat/vel` (466, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
