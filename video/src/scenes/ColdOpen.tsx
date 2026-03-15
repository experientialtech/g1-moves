import React from "react";
import { AbsoluteFill, interpolate, OffthreadVideo, useCurrentFrame } from "remotion";
import { COLD_OPEN_CLIPS } from "../videos";
import { COLORS } from "../styles";

export const ColdOpen: React.FC = () => {
  const frame = useCurrentFrame();
  const clipDuration = 30;
  const clipIndex = Math.min(Math.floor(frame / clipDuration), COLD_OPEN_CLIPS.length - 1);
  const clipFrame = frame % clipDuration;

  const flashOpacity = interpolate(clipFrame, [0, 3], [1, 0], { extrapolateRight: "clamp" });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <OffthreadVideo
        src={COLD_OPEN_CLIPS[clipIndex].path}
        style={{ width: "100%", height: "100%", objectFit: "cover" }}
        startFrom={30}
      />
      <AbsoluteFill style={{ backgroundColor: "white", opacity: flashOpacity }} />
    </AbsoluteFill>
  );
};
