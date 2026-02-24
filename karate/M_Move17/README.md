# M_Move17

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 26.63s | **Frames:** 1598

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
| Joint velocity (max) | 62.79 rad/s |
| Root displacement | 5.40 m |
| Root velocity (mean) | 0.20 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1598, 3), `root_rot` (1598, 4), `dof_pos` (1598, 29)
- **NPZ**: Training data — `joint_pos/vel` (1597, 29), `body_pos/quat/vel` (1597, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
