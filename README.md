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
| `<clip>_bl.fbx` | FBX for Blender |
| `<clip>_mb.fbx` | FBX for Maya |
| `<clip>_ue.fbx` | FBX for Unreal Engine |
| `<clip>_un.fbx` | FBX for Unity |

## Clips

### Dance (28)

| Clip | Source |
|------|--------|
| B_DadDance | Bonus |
| B_LongDance | Bonus |
| B_SpiralDance | Bonus |
| B_StretchDance | Bonus |
| B_WiggleDance | Bonus |
| J_Dance0_StepTouch | Dance |
| J_Dance1_Modern | Dance |
| J_Dance2_Salsa | Dance |
| J_Dance3_Woah | Dance |
| J_Dance4_Broadway | Dance |
| J_Dance5_Hype | Dance |
| J_Dance6_Sassy | Dance |
| J_Dance7_Party | Dance |
| J_Dance8_WestCoast | Dance |
| J_Dance9_PeaceMaker | Dance |
| J_Dance11_Gnarly | Dance |
| J_Dance12_LushLife | Dance |
| J_Dance17_Shuffle | Dance |
| J_Dance18_TikTok | Dance |
| J_Dance19_LetsGO | Dance |
| J_Dance20_DWG | Dance |
| J_Dance21_Blunt | Dance |
| J_Dance22_Thrilling | Dance |
| J_Dance23_MidnightSun | Dance |
| J_ShortDance13_SingleLadies | Dance |
| J_ShortDance14_Disco | Dance |
| J_ShortDance15_Nineties | Dance |
| J_ShortDance16_JazzWalk | Dance |

### Karate (27)

| Clip | Source |
|------|--------|
| B_AttackKarate | Bonus |
| B_BowKarate | Bonus |
| B_ChopsKarate | Bonus |
| B_CrazyChopsKarate | Bonus |
| B_ForwardKarate | Bonus |
| B_LongKarate | Bonus |
| B_SpinKarate | Bonus |
| M_Dance1 | Karate |
| M_Dance2 | Karate |
| M_Dance3 | Karate |
| M_Dance4 | Karate |
| M_Dance5 | Karate |
| M_Dance6 | Karate |
| M_Dance7 | Karate |
| M_Dance8 | Karate |
| M_Dance9 | Karate |
| M_Dance10 | Karate |
| M_Dance11 | Karate |
| M_Dance17 | Karate |
| M_Dance18 | Karate |
| M_Dance19 | Karate |
| M_Dance20 | Karate |
| M_ShortDance12 | Karate |
| M_ShortDance13 | Karate |
| M_ShortDance14 | Karate |
| M_ShortDance15 | Karate |
| M_ShortDance16 | Karate |

### Bonus (4)

| Clip | Description |
|------|-------------|
| B_Fence1 | Fencing |
| B_Fence3 | Fencing |
| B_HandsChop | Hand chop |
| B_HandsUp | Hands up |

## Capture Details

- **Tool**: Movin Studio
- **Skeleton**: Humanoid, Hips root, 6-DOF root channels, 3-DOF joint rotations (YXZ)
- **Export formats**: BVH + 4 FBX variants (Blender, Maya, Unreal, Unity)
