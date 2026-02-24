# M_Move10

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 30.53s | **Frames:** 1832

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
| Joint velocity (max) | 36.39 rad/s |
| Root displacement | 16.31 m |
| Root velocity (mean) | 0.53 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1832, 3), `root_rot` (1832, 4), `dof_pos` (1832, 29)
- **NPZ**: Training data — `joint_pos/vel` (1831, 29), `body_pos/quat/vel` (1831, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
