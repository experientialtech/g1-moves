# M_ShortMove16

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 7.38s | **Frames:** 443

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 1.14 rad/s |
| Joint velocity (max) | 79.12 rad/s |
| Root displacement | 3.83 m |
| Root velocity (mean) | 0.52 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (443, 3), `root_rot` (443, 4), `dof_pos` (443, 29)
- **NPZ**: Training data — `joint_pos/vel` (442, 29), `body_pos/quat/vel` (442, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
