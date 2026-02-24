# B_AttackKarate

**Category:** Karate | **Performer:** Mitch Chaiet | **Duration:** 47.18s | **Frames:** 2831

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.50 rad/s |
| Joint velocity (max) | 81.96 rad/s |
| Root displacement | 13.25 m |
| Root velocity (mean) | 0.28 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2831, 3), `root_rot` (2831, 4), `dof_pos` (2831, 29)
- **NPZ**: Training data — `joint_pos/vel` (2830, 29), `body_pos/quat/vel` (2830, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
