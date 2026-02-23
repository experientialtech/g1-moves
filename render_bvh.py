"""Fast BVH to MP4 renderer using PIL + ffmpeg pipe."""
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw

WIDTH, HEIGHT = 640, 640
BG_COLOR = (0, 0, 0)
BONE_COLOR = (0, 255, 170)
JOINT_COLOR = (0, 255, 170)
JOINT_RADIUS = 3
BONE_WIDTH = 3


def parse_bvh(filepath):
    with open(filepath) as f:
        lines = f.readlines()

    joints = []
    parent_stack = []
    joint_offsets = {}
    joint_channels = {}
    joint_parents = {}
    channel_order = []
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('ROOT') or line.startswith('JOINT'):
            name = line.split()[-1]
            joints.append(name)
            joint_parents[name] = parent_stack[-1] if parent_stack else None
        elif line.startswith('End Site'):
            name = parent_stack[-1] + '_End'
            joints.append(name)
            joint_parents[name] = parent_stack[-1]
        elif line.startswith('OFFSET'):
            vals = list(map(float, line.split()[1:]))
            joint_offsets[joints[-1]] = np.array(vals)
        elif line.startswith('CHANNELS'):
            parts = line.split()
            n_ch = int(parts[1])
            ch_names = parts[2:2+n_ch]
            joint_channels[joints[-1]] = ch_names
            for ch in ch_names:
                channel_order.append((joints[-1], ch))
        elif line == '{':
            if joints:
                parent_stack.append(joints[-1])
        elif line == '}':
            if parent_stack:
                parent_stack.pop()
        elif line.startswith('MOTION'):
            i += 1
            break
        i += 1

    n_frames = int(lines[i].split(':')[1])
    i += 1
    frame_time = float(lines[i].split(':')[1])
    i += 1

    frames = []
    while i < len(lines):
        line = lines[i].strip()
        if line:
            frames.append(list(map(float, line.split())))
        i += 1

    return joints, joint_offsets, joint_channels, joint_parents, channel_order, np.array(frames), n_frames, frame_time


# Precompute rotation matrices for common angles
def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1,0,0],[0,c,-s],[0,s,c]])

def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c,0,s],[0,1,0],[-s,0,c]])

def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c,-s,0],[s,c,0],[0,0,1]])

ROT_FN = {'X': rot_x, 'Y': rot_y, 'Z': rot_z}


def compute_all_positions(frames, joints, offsets, channels, parents, ch_order):
    """Vectorized position computation for all frames."""
    n_frames = len(frames)
    n_joints = len(joints)
    joint_idx = {j: i for i, j in enumerate(joints)}

    # Build channel mapping
    ch_map = {}
    ci = 0
    for joint, ch_name in ch_order:
        if joint not in ch_map:
            ch_map[joint] = {}
        ch_map[joint][ch_name] = ci
        ci += 1

    all_positions = np.zeros((n_frames, n_joints, 3))

    for fi in range(n_frames):
        fd = frames[fi]
        positions = {}
        rotations = {}

        for joint in joints:
            parent = parents[joint]
            offset = offsets.get(joint, np.zeros(3))

            if parent is None:
                cm = ch_map.get(joint, {})
                tx = fd[cm['Xposition']] if 'Xposition' in cm else 0
                ty = fd[cm['Yposition']] if 'Yposition' in cm else 0
                tz = fd[cm['Zposition']] if 'Zposition' in cm else 0
                p_pos = np.array([tx, ty, tz])
                p_rot = np.eye(3)
            else:
                p_pos = positions[parent]
                p_rot = rotations[parent]

            pos = p_pos + p_rot @ offset

            local_rot = np.eye(3)
            if joint in channels and joint in ch_map:
                for ch in channels[joint]:
                    if 'rotation' in ch.lower():
                        axis = ch[0]
                        val = np.radians(fd[ch_map[joint][ch]])
                        local_rot = local_rot @ ROT_FN[axis](val)

            rotations[joint] = p_rot @ local_rot
            positions[joint] = pos
            all_positions[fi, joint_idx[joint]] = pos

    return all_positions


def project(pos_3d, center, scale):
    """Simple orthographic projection: X right, Y up, looking from front-ish."""
    # Rotate slightly for a 3/4 view
    angle = np.radians(30)
    c, s = np.cos(angle), np.sin(angle)
    x = pos_3d[:, 0] * c + pos_3d[:, 2] * s
    y = pos_3d[:, 1]
    # Map to screen
    sx = (x - center[0]) * scale + WIDTH / 2
    sy = HEIGHT / 2 - (y - center[1]) * scale
    return np.column_stack([sx, sy])


def main():
    bvh_path = sys.argv[1] if len(sys.argv) > 1 else 'dance/J_Dance3_Woah/J_Dance3_Woah.bvh'
    out_path = sys.argv[2] if len(sys.argv) > 2 else bvh_path.rsplit('.', 1)[0] + '.mp4'

    print(f"Parsing {bvh_path}...")
    joints, offsets, channels, parents, ch_order, frames, n_frames, frame_time = parse_bvh(bvh_path)

    # Filter joints
    finger_keywords = ['Index', 'Middle', 'Ring', 'Pinky', 'Thumb']
    major_mask = [i for i, j in enumerate(joints) if '_End' not in j and not any(k in j for k in finger_keywords)]
    major_joints = [joints[i] for i in major_mask]
    major_set = set(major_mask)

    bones = []
    joint_idx = {j: i for i, j in enumerate(joints)}
    for j in major_joints:
        p = parents[j]
        if p is not None and joint_idx[p] in major_set:
            bones.append((joint_idx[p], joint_idx[j]))

    # Subsample for speed
    step = 2
    sampled = frames[::step]
    fps = 1.0 / (frame_time * step)

    print(f"Computing positions for {len(sampled)} frames...")
    all_pos = compute_all_positions(sampled, joints, offsets, channels, parents, ch_order)

    # Compute projection params from all major joint positions
    major_pos = all_pos[:, major_mask, :]
    flat = major_pos.reshape(-1, 3)

    angle = np.radians(30)
    c, s = np.cos(angle), np.sin(angle)
    proj_x = flat[:, 0] * c + flat[:, 2] * s
    proj_y = flat[:, 1]

    cx = (proj_x.min() + proj_x.max()) / 2
    cy = (proj_y.min() + proj_y.max()) / 2
    rx = (proj_x.max() - proj_x.min()) / 2
    ry = (proj_y.max() - proj_y.min()) / 2
    max_r = max(rx, ry) * 1.3
    scale = (min(WIDTH, HEIGHT) / 2) / max_r if max_r > 0 else 1
    center = np.array([cx, cy])

    print(f"Rendering to {out_path} at {fps:.0f} fps...")
    proc = subprocess.Popen([
        'ffmpeg', '-y',
        '-f', 'rawvideo', '-pix_fmt', 'rgb24',
        '-s', f'{WIDTH}x{HEIGHT}',
        '-r', str(int(round(fps))),
        '-i', '-',
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
        '-pix_fmt', 'yuv420p',
        out_path
    ], stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    for fi in range(len(sampled)):
        pts = project(all_pos[fi], center, scale)

        img = Image.new('RGB', (WIDTH, HEIGHT), BG_COLOR)
        draw = ImageDraw.Draw(img)

        for pi, ci in bones:
            x1, y1 = pts[pi]
            x2, y2 = pts[ci]
            draw.line([(x1, y1), (x2, y2)], fill=BONE_COLOR, width=BONE_WIDTH)

        for idx in major_mask:
            x, y = pts[idx]
            draw.ellipse([x-JOINT_RADIUS, y-JOINT_RADIUS, x+JOINT_RADIUS, y+JOINT_RADIUS],
                         fill=JOINT_COLOR)

        proc.stdin.write(np.array(img).tobytes())

    proc.stdin.close()
    proc.wait()
    print(f"Done: {out_path}")


if __name__ == '__main__':
    main()
