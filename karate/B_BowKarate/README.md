# B_BowKarate

**Category:** Karate | **Performer:** Mitch Chaiet | **Duration:** 37.57s | **Frames:** 2254

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.43 rad/s |
| Joint velocity (max) | 81.02 rad/s |
| Root displacement | 6.76 m |
| Root velocity (mean) | 0.18 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2254, 3), `root_rot` (2254, 4), `dof_pos` (2254, 29)
- **NPZ**: Training data — `joint_pos/vel` (2253, 29), `body_pos/quat/vel` (2253, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
