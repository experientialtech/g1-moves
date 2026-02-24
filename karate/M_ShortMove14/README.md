# M_ShortMove14

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 6.55s | **Frames:** 393

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.46 rad/s |
| Joint velocity (max) | 18.12 rad/s |
| Root displacement | 1.01 m |
| Root velocity (mean) | 0.15 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (393, 3), `root_rot` (393, 4), `dof_pos` (393, 29)
- **NPZ**: Training data — `joint_pos/vel` (392, 29), `body_pos/quat/vel` (392, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
