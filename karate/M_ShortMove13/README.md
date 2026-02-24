# M_ShortMove13

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 8.98s | **Frames:** 539

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.69 rad/s |
| Joint velocity (max) | 19.87 rad/s |
| Root displacement | 2.16 m |
| Root velocity (mean) | 0.24 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (539, 3), `root_rot` (539, 4), `dof_pos` (539, 29)
- **NPZ**: Training data — `joint_pos/vel` (538, 29), `body_pos/quat/vel` (538, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
