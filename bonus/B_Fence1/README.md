# B_Fence1

**Category:** Bonus | **Performer:** Mitch Chaiet | **Duration:** 27.0s | **Frames:** 1620

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |
| `policy/` | PT, MP4, GIF, agent.yaml, env.yaml, training_log.csv |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.19 rad/s |
| Joint velocity (max) | 8.98 rad/s |
| Root displacement | 4.96 m |
| Root velocity (mean) | 0.18 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (1620, 3), `root_rot` (1620, 4), `dof_pos` (1620, 29)
- **NPZ**: Training data — `joint_pos/vel` (1619, 29), `body_pos/quat/vel` (1619, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
