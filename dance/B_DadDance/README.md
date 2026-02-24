# B_DadDance

**Category:** Dance | **Performer:** Mitch Chaiet | **Duration:** 41.82s | **Frames:** 2509

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.36 rad/s |
| Joint velocity (max) | 6.48 rad/s |
| Root displacement | 5.93 m |
| Root velocity (mean) | 0.14 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2509, 3), `root_rot` (2509, 4), `dof_pos` (2509, 29)
- **NPZ**: Training data — `joint_pos/vel` (2508, 29), `body_pos/quat/vel` (2508, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
