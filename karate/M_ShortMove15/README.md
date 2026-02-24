# M_ShortMove15

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 6.8s | **Frames:** 408

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.76 rad/s |
| Joint velocity (max) | 18.59 rad/s |
| Root displacement | 2.88 m |
| Root velocity (mean) | 0.43 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (408, 3), `root_rot` (408, 4), `dof_pos` (408, 29)
- **NPZ**: Training data — `joint_pos/vel` (407, 29), `body_pos/quat/vel` (407, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
