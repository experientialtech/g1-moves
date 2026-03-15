import React from "react";
import { Composition } from "remotion";
import { loadFont as loadBebasNeue } from "@remotion/google-fonts/BebasNeue";
import { loadFont as loadIBMPlexMono } from "@remotion/google-fonts/IBMPlexMono";
import { loadFont as loadManrope } from "@remotion/google-fonts/Manrope";
import { LaunchVideo } from "./LaunchVideo";

loadBebasNeue();
loadIBMPlexMono();
loadManrope();

export const Root: React.FC = () => {
  return (
    <>
      <Composition
        id="LaunchVideo"
        component={LaunchVideo}
        durationInFrames={2718}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};
