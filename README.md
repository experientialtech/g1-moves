# G1 Moves

Motion capture clips for the Unitree G1 humanoid robot, captured with Movin Studio and exported as BVH and FBX.

## Structure

```
dance/          28 clips — dance routines
karate/         27 clips — karate/martial arts moves
bonus/           4 clips — fencing, hands-up, chops
movin-studio-project/   Raw Movin Studio recordings and project file
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

## Clips

### Dance (28)

| Clip | Preview | | Retarget |
|------|---------|--|----------|
| B_DadDance | [MP4](dance/B_DadDance/B_DadDance.mp4) | [GIF](dance/B_DadDance/B_DadDance.gif) | ![](dance/B_DadDance/B_DadDance_retarget.gif) |
| B_LongDance | [MP4](dance/B_LongDance/B_LongDance.mp4) | [GIF](dance/B_LongDance/B_LongDance.gif) | ![](dance/B_LongDance/B_LongDance_retarget.gif) |
| B_SpiralDance | [MP4](dance/B_SpiralDance/B_SpiralDance.mp4) | [GIF](dance/B_SpiralDance/B_SpiralDance.gif) | ![](dance/B_SpiralDance/B_SpiralDance_retarget.gif) |
| B_StretchDance | [MP4](dance/B_StretchDance/B_StretchDance.mp4) | [GIF](dance/B_StretchDance/B_StretchDance.gif) | ![](dance/B_StretchDance/B_StretchDance_retarget.gif) |
| B_WiggleDance | [MP4](dance/B_WiggleDance/B_WiggleDance.mp4) | [GIF](dance/B_WiggleDance/B_WiggleDance.gif) | ![](dance/B_WiggleDance/B_WiggleDance_retarget.gif) |
| J_Dance0_StepTouch | [MP4](dance/J_Dance0_StepTouch/J_Dance0_StepTouch.mp4) | [GIF](dance/J_Dance0_StepTouch/J_Dance0_StepTouch.gif) | ![](dance/J_Dance0_StepTouch/J_Dance0_StepTouch_retarget.gif) |
| J_Dance1_Modern | [MP4](dance/J_Dance1_Modern/J_Dance1_Modern.mp4) | [GIF](dance/J_Dance1_Modern/J_Dance1_Modern.gif) | ![](dance/J_Dance1_Modern/J_Dance1_Modern_retarget.gif) |
| J_Dance2_Salsa | [MP4](dance/J_Dance2_Salsa/J_Dance2_Salsa.mp4) | [GIF](dance/J_Dance2_Salsa/J_Dance2_Salsa.gif) | ![](dance/J_Dance2_Salsa/J_Dance2_Salsa_retarget.gif) |
| J_Dance3_Woah | [MP4](dance/J_Dance3_Woah/J_Dance3_Woah.mp4) | [GIF](dance/J_Dance3_Woah/J_Dance3_Woah.gif) | ![](dance/J_Dance3_Woah/J_Dance3_Woah_retarget.gif) |
| J_Dance4_Broadway | [MP4](dance/J_Dance4_Broadway/J_Dance4_Broadway.mp4) | [GIF](dance/J_Dance4_Broadway/J_Dance4_Broadway.gif) | ![](dance/J_Dance4_Broadway/J_Dance4_Broadway_retarget.gif) |
| J_Dance5_Hype | [MP4](dance/J_Dance5_Hype/J_Dance5_Hype.mp4) | [GIF](dance/J_Dance5_Hype/J_Dance5_Hype.gif) | ![](dance/J_Dance5_Hype/J_Dance5_Hype_retarget.gif) |
| J_Dance6_Sassy | [MP4](dance/J_Dance6_Sassy/J_Dance6_Sassy.mp4) | [GIF](dance/J_Dance6_Sassy/J_Dance6_Sassy.gif) | ![](dance/J_Dance6_Sassy/J_Dance6_Sassy_retarget.gif) |
| J_Dance7_Party | [MP4](dance/J_Dance7_Party/J_Dance7_Party.mp4) | [GIF](dance/J_Dance7_Party/J_Dance7_Party.gif) | ![](dance/J_Dance7_Party/J_Dance7_Party_retarget.gif) |
| J_Dance8_WestCoast | [MP4](dance/J_Dance8_WestCoast/J_Dance8_WestCoast.mp4) | [GIF](dance/J_Dance8_WestCoast/J_Dance8_WestCoast.gif) | ![](dance/J_Dance8_WestCoast/J_Dance8_WestCoast_retarget.gif) |
| J_Dance9_PeaceMaker | [MP4](dance/J_Dance9_PeaceMaker/J_Dance9_PeaceMaker.mp4) | [GIF](dance/J_Dance9_PeaceMaker/J_Dance9_PeaceMaker.gif) | ![](dance/J_Dance9_PeaceMaker/J_Dance9_PeaceMaker_retarget.gif) |
| J_Dance11_Gnarly | [MP4](dance/J_Dance11_Gnarly/J_Dance11_Gnarly.mp4) | [GIF](dance/J_Dance11_Gnarly/J_Dance11_Gnarly.gif) | ![](dance/J_Dance11_Gnarly/J_Dance11_Gnarly_retarget.gif) |
| J_Dance12_LushLife | [MP4](dance/J_Dance12_LushLife/J_Dance12_LushLife.mp4) | [GIF](dance/J_Dance12_LushLife/J_Dance12_LushLife.gif) | ![](dance/J_Dance12_LushLife/J_Dance12_LushLife_retarget.gif) |
| J_Dance17_Shuffle | [MP4](dance/J_Dance17_Shuffle/J_Dance17_Shuffle.mp4) | [GIF](dance/J_Dance17_Shuffle/J_Dance17_Shuffle.gif) | ![](dance/J_Dance17_Shuffle/J_Dance17_Shuffle_retarget.gif) |
| J_Dance18_TikTok | [MP4](dance/J_Dance18_TikTok/J_Dance18_TikTok.mp4) | [GIF](dance/J_Dance18_TikTok/J_Dance18_TikTok.gif) | ![](dance/J_Dance18_TikTok/J_Dance18_TikTok_retarget.gif) |
| J_Dance19_LetsGO | [MP4](dance/J_Dance19_LetsGO/J_Dance19_LetsGO.mp4) | [GIF](dance/J_Dance19_LetsGO/J_Dance19_LetsGO.gif) | ![](dance/J_Dance19_LetsGO/J_Dance19_LetsGO_retarget.gif) |
| J_Dance20_DWG | [MP4](dance/J_Dance20_DWG/J_Dance20_DWG.mp4) | [GIF](dance/J_Dance20_DWG/J_Dance20_DWG.gif) | ![](dance/J_Dance20_DWG/J_Dance20_DWG_retarget.gif) |
| J_Dance21_Blunt | [MP4](dance/J_Dance21_Blunt/J_Dance21_Blunt.mp4) | [GIF](dance/J_Dance21_Blunt/J_Dance21_Blunt.gif) | ![](dance/J_Dance21_Blunt/J_Dance21_Blunt_retarget.gif) |
| J_Dance22_Thrilling | [MP4](dance/J_Dance22_Thrilling/J_Dance22_Thrilling.mp4) | [GIF](dance/J_Dance22_Thrilling/J_Dance22_Thrilling.gif) | ![](dance/J_Dance22_Thrilling/J_Dance22_Thrilling_retarget.gif) |
| J_Dance23_MidnightSun | [MP4](dance/J_Dance23_MidnightSun/J_Dance23_MidnightSun.mp4) | [GIF](dance/J_Dance23_MidnightSun/J_Dance23_MidnightSun.gif) | ![](dance/J_Dance23_MidnightSun/J_Dance23_MidnightSun_retarget.gif) |
| J_ShortDance13_SingleLadies | [MP4](dance/J_ShortDance13_SingleLadies/J_ShortDance13_SingleLadies.mp4) | [GIF](dance/J_ShortDance13_SingleLadies/J_ShortDance13_SingleLadies.gif) | ![](dance/J_ShortDance13_SingleLadies/J_ShortDance13_SingleLadies_retarget.gif) |
| J_ShortDance14_Disco | [MP4](dance/J_ShortDance14_Disco/J_ShortDance14_Disco.mp4) | [GIF](dance/J_ShortDance14_Disco/J_ShortDance14_Disco.gif) | ![](dance/J_ShortDance14_Disco/J_ShortDance14_Disco_retarget.gif) |
| J_ShortDance15_Nineties | [MP4](dance/J_ShortDance15_Nineties/J_ShortDance15_Nineties.mp4) | [GIF](dance/J_ShortDance15_Nineties/J_ShortDance15_Nineties.gif) | ![](dance/J_ShortDance15_Nineties/J_ShortDance15_Nineties_retarget.gif) |
| J_ShortDance16_JazzWalk | [MP4](dance/J_ShortDance16_JazzWalk/J_ShortDance16_JazzWalk.mp4) | [GIF](dance/J_ShortDance16_JazzWalk/J_ShortDance16_JazzWalk.gif) | ![](dance/J_ShortDance16_JazzWalk/J_ShortDance16_JazzWalk_retarget.gif) |

### Karate (27)

| Clip | Preview | | Retarget |
|------|---------|--|----------|
| B_AttackKarate | [MP4](karate/B_AttackKarate/B_AttackKarate.mp4) | [GIF](karate/B_AttackKarate/B_AttackKarate.gif) | ![](karate/B_AttackKarate/B_AttackKarate_retarget.gif) |
| B_BowKarate | [MP4](karate/B_BowKarate/B_BowKarate.mp4) | [GIF](karate/B_BowKarate/B_BowKarate.gif) | ![](karate/B_BowKarate/B_BowKarate_retarget.gif) |
| B_ChopsKarate | [MP4](karate/B_ChopsKarate/B_ChopsKarate.mp4) | [GIF](karate/B_ChopsKarate/B_ChopsKarate.gif) | ![](karate/B_ChopsKarate/B_ChopsKarate_retarget.gif) |
| B_CrazyChopsKarate | [MP4](karate/B_CrazyChopsKarate/B_CrazyChopsKarate.mp4) | [GIF](karate/B_CrazyChopsKarate/B_CrazyChopsKarate.gif) | ![](karate/B_CrazyChopsKarate/B_CrazyChopsKarate_retarget.gif) |
| B_ForwardKarate | [MP4](karate/B_ForwardKarate/B_ForwardKarate.mp4) | [GIF](karate/B_ForwardKarate/B_ForwardKarate.gif) | ![](karate/B_ForwardKarate/B_ForwardKarate_retarget.gif) |
| B_LongKarate | [MP4](karate/B_LongKarate/B_LongKarate.mp4) | [GIF](karate/B_LongKarate/B_LongKarate.gif) | ![](karate/B_LongKarate/B_LongKarate_retarget.gif) |
| B_SpinKarate | [MP4](karate/B_SpinKarate/B_SpinKarate.mp4) | [GIF](karate/B_SpinKarate/B_SpinKarate.gif) | ![](karate/B_SpinKarate/B_SpinKarate_retarget.gif) |
| M_Move1 | [MP4](karate/M_Move1/M_Move1.mp4) | [GIF](karate/M_Move1/M_Move1.gif) | ![](karate/M_Move1/M_Move1_retarget.gif) |
| M_Move2 | [MP4](karate/M_Move2/M_Move2.mp4) | [GIF](karate/M_Move2/M_Move2.gif) | ![](karate/M_Move2/M_Move2_retarget.gif) |
| M_Move3 | [MP4](karate/M_Move3/M_Move3.mp4) | [GIF](karate/M_Move3/M_Move3.gif) | ![](karate/M_Move3/M_Move3_retarget.gif) |
| M_Move4 | [MP4](karate/M_Move4/M_Move4.mp4) | [GIF](karate/M_Move4/M_Move4.gif) | ![](karate/M_Move4/M_Move4_retarget.gif) |
| M_Move5 | [MP4](karate/M_Move5/M_Move5.mp4) | [GIF](karate/M_Move5/M_Move5.gif) | ![](karate/M_Move5/M_Move5_retarget.gif) |
| M_Move6 | [MP4](karate/M_Move6/M_Move6.mp4) | [GIF](karate/M_Move6/M_Move6.gif) | ![](karate/M_Move6/M_Move6_retarget.gif) |
| M_Move7 | [MP4](karate/M_Move7/M_Move7.mp4) | [GIF](karate/M_Move7/M_Move7.gif) | ![](karate/M_Move7/M_Move7_retarget.gif) |
| M_Move8 | [MP4](karate/M_Move8/M_Move8.mp4) | [GIF](karate/M_Move8/M_Move8.gif) | ![](karate/M_Move8/M_Move8_retarget.gif) |
| M_Move9 | [MP4](karate/M_Move9/M_Move9.mp4) | [GIF](karate/M_Move9/M_Move9.gif) | ![](karate/M_Move9/M_Move9_retarget.gif) |
| M_Move10 | [MP4](karate/M_Move10/M_Move10.mp4) | [GIF](karate/M_Move10/M_Move10.gif) | ![](karate/M_Move10/M_Move10_retarget.gif) |
| M_Move11 | [MP4](karate/M_Move11/M_Move11.mp4) | [GIF](karate/M_Move11/M_Move11.gif) | ![](karate/M_Move11/M_Move11_retarget.gif) |
| M_Move17 | [MP4](karate/M_Move17/M_Move17.mp4) | [GIF](karate/M_Move17/M_Move17.gif) | ![](karate/M_Move17/M_Move17_retarget.gif) |
| M_Move18 | [MP4](karate/M_Move18/M_Move18.mp4) | [GIF](karate/M_Move18/M_Move18.gif) | ![](karate/M_Move18/M_Move18_retarget.gif) |
| M_Move19 | [MP4](karate/M_Move19/M_Move19.mp4) | [GIF](karate/M_Move19/M_Move19.gif) | ![](karate/M_Move19/M_Move19_retarget.gif) |
| M_Move20 | [MP4](karate/M_Move20/M_Move20.mp4) | [GIF](karate/M_Move20/M_Move20.gif) | ![](karate/M_Move20/M_Move20_retarget.gif) |
| M_ShortMove12 | [MP4](karate/M_ShortMove12/M_ShortMove12.mp4) | [GIF](karate/M_ShortMove12/M_ShortMove12.gif) | ![](karate/M_ShortMove12/M_ShortMove12_retarget.gif) |
| M_ShortMove13 | [MP4](karate/M_ShortMove13/M_ShortMove13.mp4) | [GIF](karate/M_ShortMove13/M_ShortMove13.gif) | ![](karate/M_ShortMove13/M_ShortMove13_retarget.gif) |
| M_ShortMove14 | [MP4](karate/M_ShortMove14/M_ShortMove14.mp4) | [GIF](karate/M_ShortMove14/M_ShortMove14.gif) | ![](karate/M_ShortMove14/M_ShortMove14_retarget.gif) |
| M_ShortMove15 | [MP4](karate/M_ShortMove15/M_ShortMove15.mp4) | [GIF](karate/M_ShortMove15/M_ShortMove15.gif) | ![](karate/M_ShortMove15/M_ShortMove15_retarget.gif) |
| M_ShortMove16 | [MP4](karate/M_ShortMove16/M_ShortMove16.mp4) | [GIF](karate/M_ShortMove16/M_ShortMove16.gif) | ![](karate/M_ShortMove16/M_ShortMove16_retarget.gif) |

### Bonus (4)

| Clip | Preview | | Retarget |
|------|---------|--|----------|
| B_Fence1 | [MP4](bonus/B_Fence1/B_Fence1.mp4) | [GIF](bonus/B_Fence1/B_Fence1.gif) | ![](bonus/B_Fence1/B_Fence1_retarget.gif) |
| B_Fence3 | [MP4](bonus/B_Fence3/B_Fence3.mp4) | [GIF](bonus/B_Fence3/B_Fence3.gif) | ![](bonus/B_Fence3/B_Fence3_retarget.gif) |
| B_HandsChop | [MP4](bonus/B_HandsChop/B_HandsChop.mp4) | [GIF](bonus/B_HandsChop/B_HandsChop.gif) | ![](bonus/B_HandsChop/B_HandsChop_retarget.gif) |
| B_HandsUp | [MP4](bonus/B_HandsUp/B_HandsUp.mp4) | [GIF](bonus/B_HandsUp/B_HandsUp.gif) | ![](bonus/B_HandsUp/B_HandsUp_retarget.gif) |

## Capture Details

- **Tool**: Movin Studio
- **Skeleton**: Humanoid, Hips root, 6-DOF root channels, 3-DOF joint rotations (YXZ)
- **Export formats**: BVH + 4 FBX variants (Blender, Maya, Unreal, Unity)
