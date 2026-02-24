# Dataset Metadata System Design

**Date:** 2026-02-24
**Status:** Approved

## Problem

The g1-moves repository contains 59 motion capture clips with consistent file structure but no machine-readable metadata, quality validation, or per-clip documentation. Researchers can't filter clips by duration or difficulty, artists can't quickly understand what each clip contains, and there's no standard dataset card for citation or discoverability.

## Design

### Deliverables

| File | Purpose | Audience |
|------|---------|----------|
| `manifest.json` | Per-clip metadata index | Researchers, tooling |
| `quality_report.json` | Automated validation results | Researchers, CI |
| `DATASET_CARD.md` | HuggingFace-style dataset card | Everyone |
| `<clip>/README.md` | Per-clip summary (59 files) | Artists, browsing |
| `generate_metadata.py` | Regeneration script | Maintainers |

### 1. manifest.json

Single JSON file at repo root. Contains dataset-level stats and per-clip metadata extracted programmatically from BVH, PKL, CSV, and NPZ files.

**Dataset-level fields:**
- `version`, `generated` (ISO timestamp)
- `robot`: "unitree_g1", `dof`: 29, `mode`: 15
- `total_clips`, `total_duration_s`, `total_frames`
- `categories`: summary counts per category
- `capture_system`: "MOVIN TRACIN"
- `retarget_sdk`: "movin_sdk_python"

**Per-clip fields:**
- `category`: dance | karate | bonus
- `performer`: name from credits
- `frames`: BVH frame count
- `fps`: 60
- `duration_s`: computed from frames/fps
- `bvh_joints`: skeleton joint count (51)
- `retarget_dof`: G1 joint count (29)
- `training_frames`: NPZ frame count (frames - 1 due to velocity computation)
- `file_sizes`: dict of key file sizes in bytes
- `joint_range`: per-DOF min/max across all frames from PKL
- `root_displacement_m`: total distance traveled by root
- `motion_stats`:
  - `mean_joint_velocity`: average absolute joint velocity (energy proxy)
  - `max_joint_velocity`: peak joint velocity (difficulty proxy)
  - `mean_root_velocity`: average root linear velocity
- `has_policy`: boolean
- `pipeline_stages`: list of completed stages ["capture", "retarget", "training", "policy"]

### 2. quality_report.json

Automated checks run across all 59 clips:

- **joint_limit_violations**: count frames where retargeted angles exceed G1 joint limits (from URDF), report worst joint and max excess
- **ground_penetration**: count frames where any foot link Z < 0 in NPZ body_pos_w
- **frame_count_consistency**: verify PKL frames == BVH frames, NPZ frames == BVH frames - 1
- **file_completeness**: all expected files present per pipeline stage
- **nan_check**: verify no NaN values in PKL or NPZ arrays

Each check produces per-clip results. Summary section lists clips as passed/warning/error.

### 3. DATASET_CARD.md

HuggingFace dataset card format:
- Dataset summary
- Supported tasks and leaderboards
- Dataset structure (directory layout + file format schemas)
- Data collection process (equipment, performers, pipeline)
- File format documentation:
  - BVH: skeleton hierarchy, channel order, frame rate
  - PKL: `{fps, root_pos, root_rot, dof_pos}` shapes and conventions
  - CSV: 36 columns (3 root pos + 4 root quat + 29 joint angles), no header
  - NPZ: `{fps, joint_pos, joint_vel, body_pos_w, body_quat_w, body_lin_vel_w, body_ang_vel_w}` shapes
  - FBX: 4 variants (Blender, Maya, Unreal, Unity)
- Usage examples (Python snippets to load each format)
- Citation BibTeX
- License
- Acknowledgements

### 4. Per-clip README.md

Generated inside each of the 59 clip folders. Short, templated:

```markdown
# B_Fence1

**Category:** Bonus | **Performer:** Mitch Chaiet | **Duration:** 27.0s | **Frames:** 1620

Fencing motion capture clip.

## Files

| Stage | Files |
|-------|-------|
| capture/ | BVH, MP4, GIF, 4x FBX |
| retarget/ | PKL, CSV, MP4, GIF |
| training/ | NPZ, MP4, GIF |
| policy/ | PT, MP4, GIF, agent.yaml, env.yaml, training_log.csv |

## Motion Stats

- Joint velocity (mean): 1.23 rad/s
- Joint velocity (max): 8.45 rad/s
- Root displacement: 2.34 m
```

### 5. generate_metadata.py

Single script with no dependencies beyond numpy and standard library. Reads all clips, computes everything, writes:
- `manifest.json`
- `quality_report.json`
- `<clip>/README.md` for each clip

Run: `python generate_metadata.py`

Flags:
- `--skip-quality`: skip validation checks (faster)
- `--clips PATTERN`: only process matching clips

## Performer Mapping

Derived from README credits and clip name prefixes:
- `B_*` in dance/bonus: Mitch Chaiet (director, performed bonus and some dance clips)
- `J_*`: Jasmine Coro (dance)
- `M_*`: Mike Gassaway (karate)

## Implementation Order

1. `generate_metadata.py` with manifest generation
2. Per-clip README generation
3. Quality report generation
4. `DATASET_CARD.md` (manual + generated stats)
5. Commit all generated files
