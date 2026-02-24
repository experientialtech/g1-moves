# B_ForwardKarate

**Category:** Karate | **Performer:** Mitch Chaiet | **Duration:** 36.33s | **Frames:** 2180

## Files

| Stage | Files |
|-------|-------|
| `capture/` | BVH, MP4, GIF, 4x FBX |
| `retarget/` | PKL, CSV, MP4, GIF |
| `training/` | NPZ, MP4, GIF |

## Motion Stats

| Metric | Value |
|--------|-------|
| Joint velocity (mean) | 0.54 rad/s |
| Joint velocity (max) | 50.43 rad/s |
| Root displacement | 10.02 m |
| Root velocity (mean) | 0.28 m/s |

## Formats

- **BVH**: Motion capture with 51-joint humanoid skeleton, 60 FPS
- **PKL**: Retargeted G1 trajectories — `root_pos` (2180, 3), `root_rot` (2180, 4), `dof_pos` (2180, 29)
- **NPZ**: Training data — `joint_pos/vel` (2179, 29), `body_pos/quat/vel` (2179, 30, 3/4)
- **FBX**: Blender (`_bl`), Maya (`_mb`), Unreal (`_ue`), Unity (`_un`)
