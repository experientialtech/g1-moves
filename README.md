<p align="center">
  <img src="logo.png" alt="Experiential Technologies" width="500">
</p>

# G1 Moves

Motion capture clips for the Unitree G1 humanoid robot, captured with Movin Studio and exported as BVH and FBX.

## Credits

**Director:** [Mitch Chaiet](https://mitchchaiet.com/)
**DIT:** [Molly Maguire](https://www.linkedin.com/in/mollymaguire001/)
**Dance:** [Jasmine Coro](https://jasminecoro.com/)
**Karate:** [Mike Gassaway](https://www.backstage.com/u/mike-gassaway/)

## Structure

```
dance/                          28 clips — dance routines
  B_DadDance/
  B_LongDance/
  B_SpiralDance/
  B_StretchDance/
  B_WiggleDance/
  J_Dance0_StepTouch/
  J_Dance1_Modern/
  J_Dance2_Salsa/
  J_Dance3_Woah/
  J_Dance4_Broadway/
  J_Dance5_Hype/
  J_Dance6_Sassy/
  J_Dance7_Party/
  J_Dance8_WestCoast/
  J_Dance9_PeaceMaker/
  J_Dance11_Gnarly/
  J_Dance12_LushLife/
  J_Dance17_Shuffle/
  J_Dance18_TikTok/
  J_Dance19_LetsGO/
  J_Dance20_DWG/
  J_Dance21_Blunt/
  J_Dance22_Thrilling/
  J_Dance23_MidnightSun/
  J_ShortDance13_SingleLadies/
  J_ShortDance14_Disco/
  J_ShortDance15_Nineties/
  J_ShortDance16_JazzWalk/
karate/                         27 clips — karate/martial arts moves
  B_AttackKarate/
  B_BowKarate/
  B_ChopsKarate/
  B_CrazyChopsKarate/
  B_ForwardKarate/
  B_LongKarate/
  B_SpinKarate/
  M_Move1/                — Guard Combo
  M_Move2/                — Low Punch
  M_Move3/                — Horse Stance
  M_Move4/                — Spin Punch
  M_Move5/                — Twist Punch
  M_Move6/                — Spin Strike
  M_Move7/                — Rapid Punch
  M_Move8/                — Drop Spin
  M_Move9/                — Level Change
  M_Move10/               — Side Kick
  M_Move11/               — Blitz
  M_Move17/               — Double Strike
  M_Move18/               — Front Kick
  M_Move19/               — Slow Kata
  M_Move20/               — Open Strike
  M_ShortMove12/          — Quick Jab
  M_ShortMove13/          — Snap Kick
  M_ShortMove14/          — Light Punch
  M_ShortMove15/          — Drop Strike
  M_ShortMove16/          — Power Burst
bonus/                           4 clips — fencing, hands-up, chops
  B_Fence1/
  B_Fence2/
  B_HandsChop/
  B_HandsUp/
movin-studio-project/           Raw Movin Studio recordings and project file
```

Each clip lives in its own subfolder containing:

| File | Format |
|------|--------|
| `<clip>.bvh` | BVH motion capture (humanoid skeleton, Hips root) |
| `<clip>.pkl` | Retargeted G1 joint trajectories (29 DOF) |
| `<clip>_bl.fbx` | FBX for Blender |
| `<clip>_mb.fbx` | FBX for Maya |
| `<clip>_ue.fbx` | FBX for Unreal Engine |
| `<clip>_un.fbx` | FBX for Unity |

## Retarget

All 59 BVH clips have been retargeted to the Unitree G1 (mode 15, 29 DOF) using [movin_sdk_python](https://github.com/MOVIN3D/movin_sdk_python). The pipeline:

1. **BVH → IK**: Per-frame inverse kinematics maps human skeleton to G1 joint limits (1.75m human height)
2. **Ground calibration**: MuJoCo forward kinematics finds minimum foot Z across all frames, shifts root down for ground contact
3. **PKL output**: `{fps, root_pos, root_rot, dof_pos}` — 60 FPS, quaternions in xyzw order, 29 joint angles
4. **Video render**: MuJoCo offscreen 1080x1080, libx264 CRF 18

Run `python retarget_all.py` to regenerate (skips existing outputs).

## Equipment

### Motion Capture

All 59 clips were captured using the [MOVIN TRACIN](https://movin3d.com/) markerless motion capture system from [MOVIN3D](https://movin3d.com/). MOVIN TRACIN uses on-device AI to fuse LiDAR point clouds and vision into production-ready motion data — no markers, no suit, no multi-camera rig. Captured performances were recorded and exported using [MOVIN Studio](https://www.movin3d.com/studio), which provides real-time skeleton visualization, recording management, and export to BVH and FBX formats. Retargeting from human skeleton to G1 robot joint space was performed using [movin_sdk_python](https://github.com/MOVIN3D/movin_sdk_python).

Thank you to [MOVIN3D](https://movin3d.com/) for building an incredible motion capture platform that makes professional-grade mocap accessible to robotics researchers.

### Workstation

All data was captured and policies were trained on a [Dell Pro Max Tower T2](https://creatorfolio.co/mitchbookpro) workstation from [Dell Technologies](https://www.dell.com/):

| Component | Spec |
|-----------|------|
| CPU | Intel Core Ultra 9 285K (24 cores, up to 7.2 GHz) |
| GPU | NVIDIA RTX PRO 6000 Blackwell Workstation Edition (96 GB GDDR7) |
| RAM | 128 GB DDR5 |
| Storage | 2x 4 TB WD SN8000S NVMe SSD (8 TB total) |
| OS | Ubuntu 24.04 LTS |

The RTX PRO 6000 Blackwell with 96 GB of VRAM enables running thousands of parallel MuJoCo-Warp simulation environments on a single GPU for reinforcement learning training, while the 24-core Ultra 9 285K handles motion retargeting and data processing. Thank you to [Dell Technologies](https://www.dell.com/) for providing the compute power behind this project.

## Clips

### Dance (28)

| Mocap | Retarget | Training |
|-------|----------|----------|
| **B_DadDance** | | |
| ![](dance/B_DadDance/capture/B_DadDance.gif) | ![](dance/B_DadDance/retarget/B_DadDance_retarget.gif) | ![](dance/B_DadDance/training/B_DadDance_training.gif) |
| **B_LongDance** | | |
| ![](dance/B_LongDance/capture/B_LongDance.gif) | ![](dance/B_LongDance/retarget/B_LongDance_retarget.gif) | ![](dance/B_LongDance/training/B_LongDance_training.gif) |
| **B_SpiralDance** | | |
| ![](dance/B_SpiralDance/capture/B_SpiralDance.gif) | ![](dance/B_SpiralDance/retarget/B_SpiralDance_retarget.gif) | ![](dance/B_SpiralDance/training/B_SpiralDance_training.gif) |
| **B_StretchDance** | | |
| ![](dance/B_StretchDance/capture/B_StretchDance.gif) | ![](dance/B_StretchDance/retarget/B_StretchDance_retarget.gif) | ![](dance/B_StretchDance/training/B_StretchDance_training.gif) |
| **B_WiggleDance** | | |
| ![](dance/B_WiggleDance/capture/B_WiggleDance.gif) | ![](dance/B_WiggleDance/retarget/B_WiggleDance_retarget.gif) | ![](dance/B_WiggleDance/training/B_WiggleDance_training.gif) |
| **J_Dance0_StepTouch** | | |
| ![](dance/J_Dance0_StepTouch/capture/J_Dance0_StepTouch.gif) | ![](dance/J_Dance0_StepTouch/retarget/J_Dance0_StepTouch_retarget.gif) | ![](dance/J_Dance0_StepTouch/training/J_Dance0_StepTouch_training.gif) |
| **J_Dance1_Modern** | | |
| ![](dance/J_Dance1_Modern/capture/J_Dance1_Modern.gif) | ![](dance/J_Dance1_Modern/retarget/J_Dance1_Modern_retarget.gif) | ![](dance/J_Dance1_Modern/training/J_Dance1_Modern_training.gif) |
| **J_Dance2_Salsa** | | |
| ![](dance/J_Dance2_Salsa/capture/J_Dance2_Salsa.gif) | ![](dance/J_Dance2_Salsa/retarget/J_Dance2_Salsa_retarget.gif) | ![](dance/J_Dance2_Salsa/training/J_Dance2_Salsa_training.gif) |
| **J_Dance3_Woah** | | |
| ![](dance/J_Dance3_Woah/capture/J_Dance3_Woah.gif) | ![](dance/J_Dance3_Woah/retarget/J_Dance3_Woah_retarget.gif) | ![](dance/J_Dance3_Woah/training/J_Dance3_Woah_training.gif) |
| **J_Dance4_Broadway** | | |
| ![](dance/J_Dance4_Broadway/capture/J_Dance4_Broadway.gif) | ![](dance/J_Dance4_Broadway/retarget/J_Dance4_Broadway_retarget.gif) | ![](dance/J_Dance4_Broadway/training/J_Dance4_Broadway_training.gif) |
| **J_Dance5_Hype** | | |
| ![](dance/J_Dance5_Hype/capture/J_Dance5_Hype.gif) | ![](dance/J_Dance5_Hype/retarget/J_Dance5_Hype_retarget.gif) | ![](dance/J_Dance5_Hype/training/J_Dance5_Hype_training.gif) |
| **J_Dance6_Sassy** | | |
| ![](dance/J_Dance6_Sassy/capture/J_Dance6_Sassy.gif) | ![](dance/J_Dance6_Sassy/retarget/J_Dance6_Sassy_retarget.gif) | ![](dance/J_Dance6_Sassy/training/J_Dance6_Sassy_training.gif) |
| **J_Dance7_Party** | | |
| ![](dance/J_Dance7_Party/capture/J_Dance7_Party.gif) | ![](dance/J_Dance7_Party/retarget/J_Dance7_Party_retarget.gif) | ![](dance/J_Dance7_Party/training/J_Dance7_Party_training.gif) |
| **J_Dance8_WestCoast** | | |
| ![](dance/J_Dance8_WestCoast/capture/J_Dance8_WestCoast.gif) | ![](dance/J_Dance8_WestCoast/retarget/J_Dance8_WestCoast_retarget.gif) | ![](dance/J_Dance8_WestCoast/training/J_Dance8_WestCoast_training.gif) |
| **J_Dance9_PeaceMaker** | | |
| ![](dance/J_Dance9_PeaceMaker/capture/J_Dance9_PeaceMaker.gif) | ![](dance/J_Dance9_PeaceMaker/retarget/J_Dance9_PeaceMaker_retarget.gif) | ![](dance/J_Dance9_PeaceMaker/training/J_Dance9_PeaceMaker_training.gif) |
| **J_Dance11_Gnarly** | | |
| ![](dance/J_Dance11_Gnarly/capture/J_Dance11_Gnarly.gif) | ![](dance/J_Dance11_Gnarly/retarget/J_Dance11_Gnarly_retarget.gif) | ![](dance/J_Dance11_Gnarly/training/J_Dance11_Gnarly_training.gif) |
| **J_Dance12_LushLife** | | |
| ![](dance/J_Dance12_LushLife/capture/J_Dance12_LushLife.gif) | ![](dance/J_Dance12_LushLife/retarget/J_Dance12_LushLife_retarget.gif) | ![](dance/J_Dance12_LushLife/training/J_Dance12_LushLife_training.gif) |
| **J_Dance17_Shuffle** | | |
| ![](dance/J_Dance17_Shuffle/capture/J_Dance17_Shuffle.gif) | ![](dance/J_Dance17_Shuffle/retarget/J_Dance17_Shuffle_retarget.gif) | ![](dance/J_Dance17_Shuffle/training/J_Dance17_Shuffle_training.gif) |
| **J_Dance18_TikTok** | | |
| ![](dance/J_Dance18_TikTok/capture/J_Dance18_TikTok.gif) | ![](dance/J_Dance18_TikTok/retarget/J_Dance18_TikTok_retarget.gif) | ![](dance/J_Dance18_TikTok/training/J_Dance18_TikTok_training.gif) |
| **J_Dance19_LetsGO** | | |
| ![](dance/J_Dance19_LetsGO/capture/J_Dance19_LetsGO.gif) | ![](dance/J_Dance19_LetsGO/retarget/J_Dance19_LetsGO_retarget.gif) | ![](dance/J_Dance19_LetsGO/training/J_Dance19_LetsGO_training.gif) |
| **J_Dance20_DWG** | | |
| ![](dance/J_Dance20_DWG/capture/J_Dance20_DWG.gif) | ![](dance/J_Dance20_DWG/retarget/J_Dance20_DWG_retarget.gif) | ![](dance/J_Dance20_DWG/training/J_Dance20_DWG_training.gif) |
| **J_Dance21_Blunt** | | |
| ![](dance/J_Dance21_Blunt/capture/J_Dance21_Blunt.gif) | ![](dance/J_Dance21_Blunt/retarget/J_Dance21_Blunt_retarget.gif) | ![](dance/J_Dance21_Blunt/training/J_Dance21_Blunt_training.gif) |
| **J_Dance22_Thrilling** | | |
| ![](dance/J_Dance22_Thrilling/capture/J_Dance22_Thrilling.gif) | ![](dance/J_Dance22_Thrilling/retarget/J_Dance22_Thrilling_retarget.gif) | ![](dance/J_Dance22_Thrilling/training/J_Dance22_Thrilling_training.gif) |
| **J_Dance23_MidnightSun** | | |
| ![](dance/J_Dance23_MidnightSun/capture/J_Dance23_MidnightSun.gif) | ![](dance/J_Dance23_MidnightSun/retarget/J_Dance23_MidnightSun_retarget.gif) | ![](dance/J_Dance23_MidnightSun/training/J_Dance23_MidnightSun_training.gif) |
| **J_ShortDance13_SingleLadies** | | |
| ![](dance/J_ShortDance13_SingleLadies/capture/J_ShortDance13_SingleLadies.gif) | ![](dance/J_ShortDance13_SingleLadies/retarget/J_ShortDance13_SingleLadies_retarget.gif) | ![](dance/J_ShortDance13_SingleLadies/training/J_ShortDance13_SingleLadies_training.gif) |
| **J_ShortDance14_Disco** | | |
| ![](dance/J_ShortDance14_Disco/capture/J_ShortDance14_Disco.gif) | ![](dance/J_ShortDance14_Disco/retarget/J_ShortDance14_Disco_retarget.gif) | ![](dance/J_ShortDance14_Disco/training/J_ShortDance14_Disco_training.gif) |
| **J_ShortDance15_Nineties** | | |
| ![](dance/J_ShortDance15_Nineties/capture/J_ShortDance15_Nineties.gif) | ![](dance/J_ShortDance15_Nineties/retarget/J_ShortDance15_Nineties_retarget.gif) | ![](dance/J_ShortDance15_Nineties/training/J_ShortDance15_Nineties_training.gif) |
| **J_ShortDance16_JazzWalk** | | |
| ![](dance/J_ShortDance16_JazzWalk/capture/J_ShortDance16_JazzWalk.gif) | ![](dance/J_ShortDance16_JazzWalk/retarget/J_ShortDance16_JazzWalk_retarget.gif) | ![](dance/J_ShortDance16_JazzWalk/training/J_ShortDance16_JazzWalk_training.gif) |

### Karate (27)

| Mocap | Retarget | Training |
|-------|----------|----------|
| **B_AttackKarate** | | |
| ![](karate/B_AttackKarate/capture/B_AttackKarate.gif) | ![](karate/B_AttackKarate/retarget/B_AttackKarate_retarget.gif) | ![](karate/B_AttackKarate/training/B_AttackKarate_training.gif) |
| **B_BowKarate** | | |
| ![](karate/B_BowKarate/capture/B_BowKarate.gif) | ![](karate/B_BowKarate/retarget/B_BowKarate_retarget.gif) | ![](karate/B_BowKarate/training/B_BowKarate_training.gif) |
| **B_ChopsKarate** | | |
| ![](karate/B_ChopsKarate/capture/B_ChopsKarate.gif) | ![](karate/B_ChopsKarate/retarget/B_ChopsKarate_retarget.gif) | ![](karate/B_ChopsKarate/training/B_ChopsKarate_training.gif) |
| **B_CrazyChopsKarate** | | |
| ![](karate/B_CrazyChopsKarate/capture/B_CrazyChopsKarate.gif) | ![](karate/B_CrazyChopsKarate/retarget/B_CrazyChopsKarate_retarget.gif) | ![](karate/B_CrazyChopsKarate/training/B_CrazyChopsKarate_training.gif) |
| **B_ForwardKarate** | | |
| ![](karate/B_ForwardKarate/capture/B_ForwardKarate.gif) | ![](karate/B_ForwardKarate/retarget/B_ForwardKarate_retarget.gif) | ![](karate/B_ForwardKarate/training/B_ForwardKarate_training.gif) |
| **B_LongKarate** | | |
| ![](karate/B_LongKarate/capture/B_LongKarate.gif) | ![](karate/B_LongKarate/retarget/B_LongKarate_retarget.gif) | ![](karate/B_LongKarate/training/B_LongKarate_training.gif) |
| **B_SpinKarate** | | |
| ![](karate/B_SpinKarate/capture/B_SpinKarate.gif) | ![](karate/B_SpinKarate/retarget/B_SpinKarate_retarget.gif) | ![](karate/B_SpinKarate/training/B_SpinKarate_training.gif) |
| **M_Move1 — Guard Combo** | | |
| ![](karate/M_Move1/capture/M_Move1.gif) | ![](karate/M_Move1/retarget/M_Move1_retarget.gif) | ![](karate/M_Move1/training/M_Move1_training.gif) |
| **M_Move2 — Low Punch** | | |
| ![](karate/M_Move2/capture/M_Move2.gif) | ![](karate/M_Move2/retarget/M_Move2_retarget.gif) | ![](karate/M_Move2/training/M_Move2_training.gif) |
| **M_Move3 — Horse Stance** | | |
| ![](karate/M_Move3/capture/M_Move3.gif) | ![](karate/M_Move3/retarget/M_Move3_retarget.gif) | ![](karate/M_Move3/training/M_Move3_training.gif) |
| **M_Move4 — Spin Punch** | | |
| ![](karate/M_Move4/capture/M_Move4.gif) | ![](karate/M_Move4/retarget/M_Move4_retarget.gif) | ![](karate/M_Move4/training/M_Move4_training.gif) |
| **M_Move5 — Twist Punch** | | |
| ![](karate/M_Move5/capture/M_Move5.gif) | ![](karate/M_Move5/retarget/M_Move5_retarget.gif) | ![](karate/M_Move5/training/M_Move5_training.gif) |
| **M_Move6 — Spin Strike** | | |
| ![](karate/M_Move6/capture/M_Move6.gif) | ![](karate/M_Move6/retarget/M_Move6_retarget.gif) | ![](karate/M_Move6/training/M_Move6_training.gif) |
| **M_Move7 — Rapid Punch** | | |
| ![](karate/M_Move7/capture/M_Move7.gif) | ![](karate/M_Move7/retarget/M_Move7_retarget.gif) | ![](karate/M_Move7/training/M_Move7_training.gif) |
| **M_Move8 — Drop Spin** | | |
| ![](karate/M_Move8/capture/M_Move8.gif) | ![](karate/M_Move8/retarget/M_Move8_retarget.gif) | ![](karate/M_Move8/training/M_Move8_training.gif) |
| **M_Move9 — Level Change** | | |
| ![](karate/M_Move9/capture/M_Move9.gif) | ![](karate/M_Move9/retarget/M_Move9_retarget.gif) | ![](karate/M_Move9/training/M_Move9_training.gif) |
| **M_Move10 — Side Kick** | | |
| ![](karate/M_Move10/capture/M_Move10.gif) | ![](karate/M_Move10/retarget/M_Move10_retarget.gif) | ![](karate/M_Move10/training/M_Move10_training.gif) |
| **M_Move11 — Blitz** | | |
| ![](karate/M_Move11/capture/M_Move11.gif) | ![](karate/M_Move11/retarget/M_Move11_retarget.gif) | ![](karate/M_Move11/training/M_Move11_training.gif) |
| **M_Move17 — Double Strike** | | |
| ![](karate/M_Move17/capture/M_Move17.gif) | ![](karate/M_Move17/retarget/M_Move17_retarget.gif) | ![](karate/M_Move17/training/M_Move17_training.gif) |
| **M_Move18 — Front Kick** | | |
| ![](karate/M_Move18/capture/M_Move18.gif) | ![](karate/M_Move18/retarget/M_Move18_retarget.gif) | ![](karate/M_Move18/training/M_Move18_training.gif) |
| **M_Move19 — Slow Kata** | | |
| ![](karate/M_Move19/capture/M_Move19.gif) | ![](karate/M_Move19/retarget/M_Move19_retarget.gif) | ![](karate/M_Move19/training/M_Move19_training.gif) |
| **M_Move20 — Open Strike** | | |
| ![](karate/M_Move20/capture/M_Move20.gif) | ![](karate/M_Move20/retarget/M_Move20_retarget.gif) | ![](karate/M_Move20/training/M_Move20_training.gif) |
| **M_ShortMove12 — Quick Jab** | | |
| ![](karate/M_ShortMove12/capture/M_ShortMove12.gif) | ![](karate/M_ShortMove12/retarget/M_ShortMove12_retarget.gif) | ![](karate/M_ShortMove12/training/M_ShortMove12_training.gif) |
| **M_ShortMove13 — Snap Kick** | | |
| ![](karate/M_ShortMove13/capture/M_ShortMove13.gif) | ![](karate/M_ShortMove13/retarget/M_ShortMove13_retarget.gif) | ![](karate/M_ShortMove13/training/M_ShortMove13_training.gif) |
| **M_ShortMove14 — Light Punch** | | |
| ![](karate/M_ShortMove14/capture/M_ShortMove14.gif) | ![](karate/M_ShortMove14/retarget/M_ShortMove14_retarget.gif) | ![](karate/M_ShortMove14/training/M_ShortMove14_training.gif) |
| **M_ShortMove15 — Drop Strike** | | |
| ![](karate/M_ShortMove15/capture/M_ShortMove15.gif) | ![](karate/M_ShortMove15/retarget/M_ShortMove15_retarget.gif) | ![](karate/M_ShortMove15/training/M_ShortMove15_training.gif) |
| **M_ShortMove16 — Power Burst** | | |
| ![](karate/M_ShortMove16/capture/M_ShortMove16.gif) | ![](karate/M_ShortMove16/retarget/M_ShortMove16_retarget.gif) | ![](karate/M_ShortMove16/training/M_ShortMove16_training.gif) |

### Bonus (4)

| Mocap | Retarget | Training | Policy |
|-------|----------|----------|--------|
| **B_Fence1** | | | |
| ![](bonus/B_Fence1/capture/B_Fence1.gif) | ![](bonus/B_Fence1/retarget/B_Fence1_retarget.gif) | ![](bonus/B_Fence1/training/B_Fence1_training.gif) | ![](bonus/B_Fence1/policy/B_Fence1_policy.gif) |
| **B_Fence2** | | | |
| ![](bonus/B_Fence2/capture/B_Fence2.gif) | ![](bonus/B_Fence2/retarget/B_Fence2_retarget.gif) | ![](bonus/B_Fence2/training/B_Fence2_training.gif) | |
| **B_HandsChop** | | | |
| ![](bonus/B_HandsChop/capture/B_HandsChop.gif) | ![](bonus/B_HandsChop/retarget/B_HandsChop_retarget.gif) | ![](bonus/B_HandsChop/training/B_HandsChop_training.gif) | |
| **B_HandsUp** | | | |
| ![](bonus/B_HandsUp/capture/B_HandsUp.gif) | ![](bonus/B_HandsUp/retarget/B_HandsUp_retarget.gif) | ![](bonus/B_HandsUp/training/B_HandsUp_training.gif) | |

## Capture Details

- **Skeleton**: Humanoid, Hips root, 6-DOF root channels, 3-DOF joint rotations (YXZ)
- **Export formats**: BVH + 4 FBX variants (Blender, Maya, Unreal, Unity)
