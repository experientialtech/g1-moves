# J_Dance20_DWG

**Category:** Dance | **Performer:** Jasmine Coro | **Duration:** 15.63s | **Frames:** 938

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
| Joint velocity (max) | 26.59 rad/s |
| Root displacement | 2.23 m |
| Root velocity (mean) | 0.14 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (938, 3), `root_rot` (938, 4), `dof_pos` (938, 29)
- **NPZ**: Training data — `joint_pos/vel` (937, 29), `body_pos/quat/vel` (937, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
