import React from "react";
import { AbsoluteFill, OffthreadVideo, interpolate, useCurrentFrame, staticFile } from "remotion";
import { COLORS } from "../styles";

export const DemoVideo: React.FC = () => {
  const frame = useCurrentFrame();

  const fadeIn = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });
  const fadeOut = interpolate(frame, [480, 510], [1, 0], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill style={{ backgroundColor: COLORS.bg }}>
      <OffthreadVideo
        src={staticFile("demo.mp4")}
        style={{
          width: "100%",
          height: "100%",
          objectFit: "cover",
          opacity: fadeIn * fadeOut,
        }}
      />
    </AbsoluteFill>
  );
};
