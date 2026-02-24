# J_ShortDance13_SingleLadies

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 14.03s | **Frames:** 842

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.42 rad/s |
| Joint velocity (max) | 9.24 rad/s |
| Root displacement | 2.11 m |
| Root velocity (mean) | 0.15 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (842, 3), `root_rot` (842, 4), `dof_pos` (842, 29)
- **NPZ**: Training data — `joint_pos/vel` (841, 29), `body_pos/quat/vel` (841, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
