# M_Move6

**Category:** Karate | **Performer:** Mike Gassaway | **Duration:** 35.62s | **Frames:** 2137

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.79 rad/s |
| Joint velocity (max) | 46.85 rad/s |
| Root displacement | 10.85 m |
| Root velocity (mean) | 0.30 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2137, 3), `root_rot` (2137, 4), `dof_pos` (2137, 29)
- **NPZ**: Training data — `joint_pos/vel` (2136, 29), `body_pos/quat/vel` (2136, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
