# M_Move8

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 14.05s | **Frames:** 843

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.93 rad/s |
| Joint velocity (max) | 25.14 rad/s |
| Root displacement | 4.31 m |
| Root velocity (mean) | 0.31 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (843, 3), `root_rot` (843, 4), `dof_pos` (843, 29)
- **NPZ**: Training data — `joint_pos/vel` (842, 29), `body_pos/quat/vel` (842, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
