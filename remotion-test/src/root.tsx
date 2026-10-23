import React from 'react';
import {Composition} from 'remotion';
import {CaixeiroCinema, PREVIEW_FRAMES} from './cinema';
export const Root: React.FC = () => (
  <Composition
    id="CaixeiroCinema"
    component={CaixeiroCinema}
    width={1080}
    height={1920}
    fps={30}
    durationInFrames={PREVIEW_FRAMES}
  />
);
