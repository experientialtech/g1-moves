import { staticFile } from "remotion";

export interface ClipDef {
  id: string;
  category: string;
  path: string;
  durationS: number;
}

/** Frame (at 30fps) at start of middle 25% of the clip */
export const midStart = (clip: ClipDef) =>
  Math.floor(clip.durationS * 30 * 0.375);

const clip = (category: string, id: string, durationS: number): ClipDef => ({
  id,
  category,
  path: staticFile(`${category}/${id}/policy/${id}_policy.mp4`),
  durationS,
});

export const DANCE_CLIPS: ClipDef[] = [
  clip("dance", "J_Dance7_Party", 15),
  clip("dance", "J_Dance5_Hype", 20),
  clip("dance", "J_Dance23_MidnightSun", 15),
  clip("dance", "B_SpiralDance", 15),
  clip("dance", "J_Dance1_Modern", 20),
  clip("dance", "J_ShortDance13_SingleLadies", 14),
  clip("dance", "J_Dance11_Gnarly", 15),
  clip("dance", "J_Dance2_Salsa", 20),
];

export const KARATE_CLIPS: ClipDef[] = [
  clip("karate", "B_CrazyChopsKarate", 20),
  clip("karate", "B_AttackKarate", 15),
  clip("karate", "B_LongKarate", 15),
  clip("karate", "M_Move4", 20),
  clip("karate", "M_Move9", 20),
  clip("karate", "B_SpinKarate", 20),
  clip("karate", "M_Move3", 20),
  clip("karate", "M_Move7", 20),
];

export const BONUS_CLIPS: ClipDef[] = [
  clip("bonus", "B_Fence1", 34),
  clip("bonus", "B_Fence2", 12),
  clip("bonus", "V_Rocamena", 9.5),
  clip("bonus", "B_HandsUp", 12),
  clip("bonus", "B_HandsChop", 12),
];

export const HERO_CLIP = clip("dance", "J_Dance5_Hype", 12);

export const COLD_OPEN_CLIPS: ClipDef[] = [
  clip("karate", "B_LongKarate", 15),
  clip("dance", "J_Dance5_Hype", 20),
  clip("bonus", "B_Fence1", 34),
];

export const HIGHLIGHT_CLIPS: ClipDef[] = [
  clip("dance", "J_Dance7_Party", 15),
  clip("karate", "B_CrazyChopsKarate", 20),
  clip("dance", "J_Dance23_MidnightSun", 15),
  clip("bonus", "B_Fence1", 34),
  clip("karate", "M_Move10", 20),
  clip("bonus", "V_Rocamena", 9.5),
];
