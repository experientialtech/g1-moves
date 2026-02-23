#!/usr/bin/env python3
"""Batch retarget all BVH clips to G1 robot PKL + render MP4/GIF previews.

Usage:
    python retarget_all.py              # process all clips, skip completed
    python retarget_all.py --force      # reprocess everything
    python retarget_all.py --workers 8  # custom parallelism
"""
import argparse
import os
import pickle
import subprocess
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import mujoco
import numpy as np
from movin_sdk_python import Retargeter, load_bvh_file

REPO_DIR = Path(__file__).resolve().parent
MUJOCO_XML = Path("/home/mitch/Repositories/g1-urdf/g1_mode15_square.xml")
CATEGORIES = ["dance", "karate", "bonus"]
HUMAN_HEIGHT = 1.75

# Rendering config
RENDER_W, RENDER_H = 1080, 1080
CAM_AZIMUTH = 90
CAM_ELEVATION = -10
CAM_DISTANCE = 2.8
CAM_LOOKAT = [0, 0, 0.65]
FFMPEG_CRF = 18

# GIF config
GIF_WIDTH = 360
GIF_FPS = 15


def discover_bvh_clips():
    """Find all BVH files under category directories."""
    clips = []
    for cat in CATEGORIES:
        cat_dir = REPO_DIR / cat
        if not cat_dir.is_dir():
            continue
        for clip_dir in sorted(cat_dir.iterdir()):
            if not clip_dir.is_dir():
                continue
            bvh_files = list(clip_dir.glob("*.bvh"))
            if bvh_files:
                clips.append(bvh_files[0])
    return clips


MIN_MP4_SIZE = 10_000  # bytes — valid MP4s are at least 10KB


def is_valid_file(path, min_size=1):
    """Check file exists and is at least min_size bytes."""
    return path.exists() and path.stat().st_size >= min_size


def is_complete(bvh_path):
    """Check if all outputs already exist and are valid for a clip."""
    stem = bvh_path.stem
    clip_dir = bvh_path.parent
    pkl = clip_dir / f"{stem}.pkl"
    mp4 = clip_dir / f"{stem}_retarget.mp4"
    gif = clip_dir / f"{stem}_retarget.gif"
    return (is_valid_file(pkl, 1000)
            and is_valid_file(mp4, MIN_MP4_SIZE)
            and is_valid_file(gif, 1000))


def retarget_bvh(bvh_path):
    """Retarget BVH to PKL with ground offset calibration."""
    frames, _, parents, bones = load_bvh_file(str(bvh_path), human_height=HUMAN_HEIGHT)
    retargeter = Retargeter(robot_type="unitree_g1", human_height=HUMAN_HEIGHT)

    n_frames = len(frames)
    root_pos = np.zeros((n_frames, 3))
    root_rot = np.zeros((n_frames, 4))  # xyzw storage
    dof_pos = np.zeros((n_frames, 29))

    for i, frame_data in enumerate(frames):
        qpos = retargeter.retarget(frame_data)
        root_pos[i] = qpos[:3]
        # MuJoCo returns wxyz, store as xyzw
        root_rot[i] = [qpos[4], qpos[5], qpos[6], qpos[3]]
        dof_pos[i] = qpos[7:]

    # Ground offset: find min foot Z via MuJoCo FK
    model = mujoco.MjModel.from_xml_path(str(MUJOCO_XML))
    data = mujoco.MjData(model)

    # Find foot geom IDs (ankle bodies)
    foot_geom_ids = []
    for gi in range(model.ngeom):
        body_name = model.body(model.geom_bodyid[gi]).name
        if "ankle" in body_name:
            foot_geom_ids.append(gi)

    min_foot_z = float("inf")
    for i in range(n_frames):
        data.qpos[:3] = root_pos[i]
        # Convert xyzw back to wxyz for MuJoCo
        data.qpos[3:7] = [root_rot[i, 3], root_rot[i, 0], root_rot[i, 1], root_rot[i, 2]]
        data.qpos[7:] = dof_pos[i]
        mujoco.mj_forward(model, data)
        for gi in foot_geom_ids:
            z = data.geom_xpos[gi, 2]
            if z < min_foot_z:
                min_foot_z = z

    # Shift root down so feet touch ground
    if min_foot_z != float("inf"):
        root_pos[:, 2] -= min_foot_z

    # BVH files in this repo are all 60fps
    pkl_data = {
        "fps": 60,
        "root_pos": root_pos,
        "root_rot": root_rot,
        "dof_pos": dof_pos,
        "local_body_pos": None,
        "link_body_list": None,
    }
    return pkl_data


def render_mp4(pkl_data, mp4_path):
    """Render motion to MP4 using MuJoCo offscreen + ffmpeg pipe."""
    model = mujoco.MjModel.from_xml_path(str(MUJOCO_XML))
    data = mujoco.MjData(model)
    renderer = mujoco.Renderer(model, height=RENDER_H, width=RENDER_W)

    root_pos = pkl_data["root_pos"]
    root_rot = pkl_data["root_rot"]
    dof_pos = pkl_data["dof_pos"]
    fps = pkl_data["fps"]
    n_frames = len(root_pos)

    proc = subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{RENDER_W}x{RENDER_H}",
            "-r", str(fps),
            "-i", "-",
            "-c:v", "libx264", "-preset", "fast", "-crf", str(FFMPEG_CRF),
            "-pix_fmt", "yuv420p",
            str(mp4_path),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    cam = mujoco.MjvCamera()
    cam.azimuth = CAM_AZIMUTH
    cam.elevation = CAM_ELEVATION
    cam.distance = CAM_DISTANCE
    cam.lookat[:] = CAM_LOOKAT

    for i in range(n_frames):
        data.qpos[:3] = root_pos[i]
        data.qpos[3:7] = [root_rot[i, 3], root_rot[i, 0], root_rot[i, 1], root_rot[i, 2]]
        data.qpos[7:] = dof_pos[i]
        mujoco.mj_forward(model, data)
        renderer.update_scene(data, cam)
        pixels = renderer.render()
        proc.stdin.write(pixels.tobytes())

    proc.stdin.close()
    proc.wait()
    renderer.close()


def create_gif(mp4_path, gif_path):
    """Create optimized GIF from MP4 using palettegen/paletteuse."""
    palette_filter = f"fps={GIF_FPS},scale={GIF_WIDTH}:-1:flags=lanczos"
    # Use per-clip palette file to avoid race conditions with multiprocessing
    palette_path = str(mp4_path).replace(".mp4", "_palette.png")
    # Two-pass: generate palette, then apply
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(mp4_path),
            "-vf", f"{palette_filter},palettegen",
            "-t", "20",  # cap at 20s to keep GIF size reasonable
            palette_path,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(mp4_path),
            "-i", palette_path,
            "-t", "20",
            "-lavfi", f"{palette_filter} [x]; [x][1:v] paletteuse",
            str(gif_path),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    # Clean up palette
    os.remove(palette_path)


def process_clip(args):
    """Process a single BVH clip through the full pipeline."""
    bvh_path, force = args
    stem = bvh_path.stem
    cat = bvh_path.parent.parent.name
    label = f"{cat}/{stem}"
    clip_dir = bvh_path.parent
    pkl_path = clip_dir / f"{stem}.pkl"
    mp4_path = clip_dir / f"{stem}_retarget.mp4"
    gif_path = clip_dir / f"{stem}_retarget.gif"

    if not force and is_complete(bvh_path):
        print(f"  [SKIP] {label} — all outputs exist", flush=True)
        return f"SKIP {label}"

    t0 = time.time()
    try:
        # Step 1: Retarget BVH → PKL
        if force or not is_valid_file(pkl_path, 1000):
            print(f"  [RETARGET] {label} — loading BVH and running IK...", flush=True)
            pkl_data = retarget_bvh(bvh_path)
            with open(pkl_path, "wb") as f:
                pickle.dump(pkl_data, f)
            n = len(pkl_data["root_pos"])
            sz = pkl_path.stat().st_size
            print(f"  [RETARGET] {label} — done: {n} frames, {sz/1024:.0f}KB pkl ({time.time()-t0:.1f}s)", flush=True)
        else:
            with open(pkl_path, "rb") as f:
                pkl_data = pickle.load(f)
            n = len(pkl_data["root_pos"])
            print(f"  [RETARGET] {label} — using existing pkl ({n} frames)", flush=True)

        # Step 2: Render MP4
        if force or not is_valid_file(mp4_path, MIN_MP4_SIZE):
            if mp4_path.exists():
                mp4_path.unlink()  # remove corrupt file
            t1 = time.time()
            print(f"  [RENDER]   {label} — rendering {n} frames to MP4...", flush=True)
            render_mp4(pkl_data, mp4_path)
            sz = mp4_path.stat().st_size
            if sz < MIN_MP4_SIZE:
                raise RuntimeError(f"Rendered MP4 too small ({sz} bytes), likely corrupt")
            print(f"  [RENDER]   {label} — done: {sz/1024/1024:.1f}MB mp4 ({time.time()-t1:.1f}s)", flush=True)
        else:
            print(f"  [RENDER]   {label} — using existing mp4", flush=True)

        # Step 3: Create GIF
        if force or not is_valid_file(gif_path, 1000):
            t2 = time.time()
            print(f"  [GIF]      {label} — generating optimized GIF...", flush=True)
            create_gif(mp4_path, gif_path)
            sz = gif_path.stat().st_size
            print(f"  [GIF]      {label} — done: {sz/1024/1024:.1f}MB gif ({time.time()-t2:.1f}s)", flush=True)
        else:
            print(f"  [GIF]      {label} — using existing gif", flush=True)

        elapsed = time.time() - t0
        print(f"  [OK]       {label} — complete ({n} frames, {elapsed:.1f}s total)", flush=True)
        return f"OK   {label} ({n} frames, {elapsed:.1f}s)"

    except Exception as e:
        elapsed = time.time() - t0
        print(f"  [FAIL]     {label} — {e} ({elapsed:.1f}s)", flush=True)
        return f"FAIL {label} ({elapsed:.1f}s): {e}"


def main():
    parser = argparse.ArgumentParser(description="Batch retarget BVH clips to G1 robot")
    parser.add_argument("--force", action="store_true", help="Reprocess all clips")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel workers")
    args = parser.parse_args()

    clips = discover_bvh_clips()
    print(f"Found {len(clips)} BVH clips")

    if not args.force:
        pending = [c for c in clips if not is_complete(c)]
        print(f"  {len(clips) - len(pending)} already complete, {len(pending)} to process")
    else:
        pending = clips

    if not pending:
        print("Nothing to do.")
        return

    work = [(c, args.force) for c in pending]

    print(f"\nStarting processing with {args.workers} workers...\n", flush=True)
    t_start = time.time()
    if args.workers == 1:
        results = [process_clip(w) for w in work]
    else:
        with Pool(args.workers) as pool:
            results = list(pool.imap_unordered(process_clip, work))

    print(f"\n{'='*60}")
    for r in sorted(results):
        print(f"  {r}")

    ok = sum(1 for r in results if r.startswith("OK"))
    fail = sum(1 for r in results if r.startswith("FAIL"))
    skip = sum(1 for r in results if r.startswith("SKIP"))
    elapsed = time.time() - t_start
    print(f"\nDone: {ok} OK, {fail} FAIL, {skip} SKIP in {elapsed:.1f}s")

    if fail > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
