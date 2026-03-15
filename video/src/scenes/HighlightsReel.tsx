import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, useCurrentFrame } from "remotion";
import { HIGHLIGHT_CLIPS, midStart } from "../videos";
import { COLORS } from "../styles";

export const HighlightsReel: React.FC = () => {
  const frame = useCurrentFrame();
  const clipDuration = 65;
  const clipIndex = Math.min(
    Math.floor(frame / clipDuration),
    HIGHLIGHT_CLIPS.length - 1
  );
  const clipFrame = frame % clipDuration;

  const opacity = interpolate(clipFrame, [0, 10, 55, 65], [0, 1, 1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <OffthreadVideo
        src={HIGHLIGHT_CLIPS[clipIndex].path}
        style={{ width: "100%", height: "100%", objectFit: "cover", opacity }}
        startFrom={midStart(HIGHLIGHT_CLIPS[clipIndex])}
      />
    </AbsoluteFill>
  );
};
