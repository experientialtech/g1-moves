# M_Move11

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 16.6s | **Frames:** 996

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 1.22 rad/s |
| Joint velocity (max) | 76.36 rad/s |
| Root displacement | 9.54 m |
| Root velocity (mean) | 0.58 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (996, 3), `root_rot` (996, 4), `dof_pos` (996, 29)
- **NPZ**: Training data — `joint_pos/vel` (995, 29), `body_pos/quat/vel` (995, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
