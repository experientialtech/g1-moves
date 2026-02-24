# B_SpinKarate

**Category:** Karate | **Performer:** Mitch Chaiet | **Duration:** 25.67s | **Frames:** 1540

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.57 rad/s |
| Joint velocity (max) | 15.96 rad/s |
| Root displacement | 7.33 m |
| Root velocity (mean) | 0.29 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1540, 3), `root_rot` (1540, 4), `dof_pos` (1540, 29)
- **NPZ**: Training data — `joint_pos/vel` (1539, 29), `body_pos/quat/vel` (1539, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
