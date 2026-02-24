# M_Move5

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 35.98s | **Frames:** 2159

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.65 rad/s |
| Joint velocity (max) | 92.96 rad/s |
| Root displacement | 13.10 m |
| Root velocity (mean) | 0.36 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2159, 3), `root_rot` (2159, 4), `dof_pos` (2159, 29)
- **NPZ**: Training data — `joint_pos/vel` (2158, 29), `body_pos/quat/vel` (2158, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
