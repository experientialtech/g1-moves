# B_WiggleDance

**Category:** Dance | **Performer:** Mitch Chaiet | **Duration:** 37.28s | **Frames:** 2237

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.26 rad/s |
| Joint velocity (max) | 8.80 rad/s |
| Root displacement | 3.53 m |
| Root velocity (mean) | 0.09 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2237, 3), `root_rot` (2237, 4), `dof_pos` (2237, 29)
- **NPZ**: Training data — `joint_pos/vel` (2236, 29), `body_pos/quat/vel` (2236, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
