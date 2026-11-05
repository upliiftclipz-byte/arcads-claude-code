import React from 'react';
import {AbsoluteFill, Audio, Composition, Sequence, staticFile, useVideoConfig} from 'remotion';
import {DURATION, VO_SLICES} from './timeline';
import {Background} from './components/primitives';
import {Captions} from './components/Captions';
import {ExampleReel} from './scenes/Example';

export const Explainer: React.FC<{captions: boolean}> = ({captions}) => (
  <AbsoluteFill>
    <Background />
    <ExampleReel />
    <Captions show={captions} />
    {VO_SLICES.length ? <VoiceOver /> : null}
  </AbsoluteFill>
);

const VoiceOver: React.FC = () => {
  const {fps} = useVideoConfig();
  return (
    <>
      {VO_SLICES.map((x) => (
        <Sequence key={x.id} from={Math.round(x.at * fps)} durationInFrames={Math.max(1, Math.round((x.to - x.from) * fps))} layout="none">
          <Audio src={staticFile('vo/vo.mp3')} startFrom={Math.round(x.from * fps)} endAt={Math.round(x.to * fps)} />
        </Sequence>
      ))}
    </>
  );
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Explainer" component={Explainer} durationInFrames={Math.round(DURATION * 30)} fps={30} width={1080} height={1920} defaultProps={{captions: true}} />
    <Composition id="Explainer60" component={Explainer} durationInFrames={Math.round(DURATION * 60)} fps={60} width={1080} height={1920} defaultProps={{captions: true}} />
  </>
);
