# M_Move18

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 16.72s | **Frames:** 1003

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.44 rad/s |
| Joint velocity (max) | 10.65 rad/s |
| Root displacement | 3.74 m |
| Root velocity (mean) | 0.22 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1003, 3), `root_rot` (1003, 4), `dof_pos` (1003, 29)
- **NPZ**: Training data — `joint_pos/vel` (1002, 29), `body_pos/quat/vel` (1002, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
