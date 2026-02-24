# J_Dance7_Party

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 46.22s | **Frames:** 2773

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.66 rad/s |
| Joint velocity (max) | 12.15 rad/s |
| Root displacement | 10.76 m |
| Root velocity (mean) | 0.23 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2773, 3), `root_rot` (2773, 4), `dof_pos` (2773, 29)
- **NPZ**: Training data — `joint_pos/vel` (2772, 29), `body_pos/quat/vel` (2772, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
