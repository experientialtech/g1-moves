# M_Move19

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 16.87s | **Frames:** 1012

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.35 rad/s |
| Joint velocity (max) | 10.84 rad/s |
| Root displacement | 2.11 m |
| Root velocity (mean) | 0.13 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1012, 3), `root_rot` (1012, 4), `dof_pos` (1012, 29)
- **NPZ**: Training data — `joint_pos/vel` (1012, 29), `body_pos/quat/vel` (1012, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
