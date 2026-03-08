# G1 Remote Controller — Button Mapping

Complete button mapping for the Unitree G1 R3 remote controller, transcribed from the physical sticker shipped with the robot (post-App Store, ~2026).

> **Official docs**: The [G1 Remote Control User Manual V1.3](https://marketing.unitree.com/article/en/G1/Remote_Control.html) (June 2025) and [G1 User Manual V1.4](https://marketing.unitree.com/article/en/G1/User_Manual.html) (August 2025) are available on Unitree's marketing CDN. This sticker includes content from the App Store launch (December 2025) that is not in those manuals.

## Activation Types

| Symbol | Meaning |
|--------|---------|
| ▲ | Long press for 2 seconds to activate |
| ★ | Single short press to activate |

## Mode Switches

| # | Mode | Button | Type |
|---|------|--------|------|
| ① | Zero Moment | Hold L2 + Click Y | ▲ ★ |
| ② | Damping | Hold L2 + Click B | ▲ ★ |
| ③ | Locked Standing | Hold L2 + Click UP | ▲ ★ |
| ④ | Lie → Stand | Hold L2 + Click X | ▲ ★ |
| ⑤ | Seated Mode | Hold L2 + Click LEFT | ▲ ★ |
| ⑥ | Squat ↔ Stand | Hold L2 + Click A | ▲ ★ |

## Locomotion

| Mode | Button |
|------|--------|
| ⑧ Running Mode | R2 + A |
| Low Speed | Double-Click L2 |
| High Speed | Double-Click L1 |
| Regular Mode (1-DOF Waist) | R1 + ⑧ |
| Regular Mode (3-DOF Waist) | R1 + ⑧ |
| Motion Control Switching | R2 + ⑧ (toggles 1-DOF / 3-DOF waist) |
| ⑧ Stepping / Standing | Double-Click START |

### Joystick Controls (in Motion Mode)

| Stick | Action |
|-------|--------|
| Left stick forward/back | Move forward / backward |
| Left stick left/right | Strafe left / right |
| Right stick left/right | Turn left / right |
| Both sticks pressed | Soft emergency stop (damping) |

### Running Controls (R2 + A active)

| Action | Button |
|--------|--------|
| Slow Running | R2 + DOWN |
| Fast Running | R2 + UP |
| Forward Lean | Hold START + Hold UP |
| Backward Lean | Hold START + Hold DOWN |

### Offset Compensation (in Main Operation)

| Direction | Button |
|-----------|--------|
| Left Offset | Hold R1 + Click → |
| Right Offset | Hold R1 + Click ← |
| Forward Offset | Hold R1 + Click ↓ |
| Backward Offset | Hold R1 + Click ↑ |

## Dance Mode & Action Packages

Enter Dance Mode first with R1 + SELECT, then trigger presets:

| Action | Button |
|--------|--------|
| ⑩ Dance Mode (enter) | R1 + SELECT |
| Kung Fu | R1 + ★ |
| Dance 1 | R1 + ★ |
| Dance 2 | R1 + ★ |
| Dance 3 | R1 + ★ |
| Roll Up | R1 + ★ |
| Jeet Kune Do | R2 + ★ |
| Twist | R2 + ★ |

> **Note**: In Dance Mode, double-click START to perform an emergency stop.

These action packages are deployed via the [Unitree Explore App](https://www.unitree.com/app/g1/) App Store (launched December 13, 2025). The three launch packages were **Bruce Lee** (Jeet Kune Do moves), **Funny Actions**, and **Twist Dance**.

## Interactive Gestures

| Action | Button |
|--------|--------|
| Handshake | SELECT + Y |
| Wave Hand | SELECT + X |
| Reject | SELECT + ★ |
| Face Wave | Double-Click ★ |
| Right Kick | Double-Click ★ |
| Clap | Double-Click ★ |
| Right Raise | Double-Click ★ |
| Flex Left | Double-Click ★ |
| Flex Right | Double-Click ★ |
| Flex Both | Double-Click ★ |
| Climb Mode | R2 + ⑧ |

> **★** marks buttons that could not be clearly identified from the sticker photo. If you have access to the physical sticker, please update with the exact face button (A/B/X/Y) or D-pad direction for each combo.

## Boot Sequences

### Standard Boot (Recommended)

```
Power On → ① Damping → ② Locked Standing → ③ Demo → Turn off
```

1. Power on the robot (short press + long press power button for 2 seconds)
2. Hold L2 + Click B → **Damping Mode** (robot goes limp with resistance)
3. Hold L2 + Click UP → **Locked Standing** (robot stands up)
4. Enter motion control → Demo / Walk
5. To shut down: Hold L2 + Click B → Damping → Power off

### Squat Boot

```
Power On → ① → ⑥ → Demo → ⑥ → Turn off
```

### Lying Boot

```
Power On (crotch post on ground) → ① → ⑤ → Demo → ⑥ → Turn off
```

### Seated Boot

```
Power On → ① → ⑥ → Turn off
```

> **Tips**:
> - ② and ③ require manual assistance to help the robot stand upright
> - Squat position startup is recommended by Unitree
> - In motion control mode, long-press ⑥ for 5 seconds to enter damping protection mode
> - Starting in lying or squatting position is only suitable for flat, hard ground

## Debug Mode (EDU Models Only)

| Action | Button |
|--------|--------|
| Enter Debug/Develop Mode | L2 + R2 (from damping state) |
| Confirm Develop Mode | L2 + A |
| Exit to Damping | L2 + B |

When in Debug Mode, the built-in motion control program is stopped, allowing SDK development without command conflicts. Press L2 + A to confirm you've entered Develop Mode. If behavior doesn't match, press L2 + R2 multiple times.

## Remote Control Hardware

| Spec | Value |
|------|-------|
| Model | R3 |
| Battery | 780 mAh lithium, ~5 hours |
| Charging | 5V / 700mA, USB-C |
| Range | 100m+ (open environment) |
| Connection | Bluetooth data transmission module |
| Auto-off | 10 minutes if not connected |

### Hardware Controls

| Function | Action |
|----------|--------|
| Power on | Short press + long press (2+ seconds) |
| Power off | Short press + long press (2+ seconds) |
| Vibration toggle | Press F3 three times quickly |
| Sound toggle | Press F3 three times quickly |
| Turn off vibration/sound | Press F1 three times quickly |
| Rocker calibration | Press F1 + F3 simultaneously, rotate sticks, press F3 to save |

## Revision History

### Remote Control User Manual

| Version | Date | Change |
|---------|------|--------|
| 1.3 | June 6, 2025 | Update of Operation Control Mode |
| 1.2 | May 15, 2025 | L2-based button combos (Y, B, UP, X, LEFT, A) |
| 1.1 | December 13, 2024 | Button Instructions Update (App Store launch) |
| 1.0 | September 3, 2024 | Initial Version |

### G1 User Manual

| Version | Date | Change |
|---------|------|--------|
| 1.4 | August 7, 2025 | Default Locomotion: R2+A, Standing/Walking: Double-tap START |
| 1.3 | July 17, 2025 | Use of Unitree Explore App |
| 1.2 | May 15, 2025 | L2-based button combos |
| 1.1 | October 28, 2024 | Parts Name — Add G1 Installation Hole Position |
| 1.0 | September 3, 2024 | Initial Version |

### Controller Firmware

| Version | Button Scheme |
|---------|---------------|
| V1.0.2 | L1-based combos (L1+B zero torque, L1+A damping, L1+UP standing) |
| V1.0.4 | L2-based combos (L2+Y zero torque, L2+B damping, L2+UP standing) |

## References

- [G1 Remote Control User Manual V1.3](https://marketing.unitree.com/article/en/G1/Remote_Control.html) — Official Unitree marketing CDN (English)
- [G1 Remote Control User Manual V1.3 (Chinese)](https://marketing.unitree.com/article/zh/G1/Remote_Control.html)
- [G1 User Manual V1.4](https://marketing.unitree.com/article/en/G1/User_Manual.html) — Official Unitree marketing CDN (English)
- [Controls (Firmware V1.0.4)](https://docs.quadruped.de/projects/g1/html/operation_1.4.html) — Third-party documentation
- [Unitree Explore App](https://www.unitree.com/app/g1/) — App Store for action packages
- [Unitree App Store announcement](https://eu.36kr.com/en/p/3595494143311879) — 36Kr coverage
