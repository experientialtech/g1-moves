# M_Move9

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 27.3s | **Frames:** 1638

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.87 rad/s |
| Joint velocity (max) | 28.41 rad/s |
| Root displacement | 14.07 m |
| Root velocity (mean) | 0.52 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1638, 3), `root_rot` (1638, 4), `dof_pos` (1638, 29)
- **NPZ**: Training data — `joint_pos/vel` (1637, 29), `body_pos/quat/vel` (1637, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
