import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, F} from '../theme';
import {CHUNKS} from '../timeline';
import {E, p, useT} from '../anim';

export const Captions: React.FC<{show: boolean}> = ({show}) => {
  const {t} = useT();
  if (!show) return null;
  const chunk = CHUNKS.find((c) => t >= c.t0 - 0.01 && t < c.t1);
  if (!chunk) return null;
  // caption ends 0.9s after last word if the next chunk is far away
  const last = chunk.words[chunk.words.length - 1].t;
  if (t > last + 1.4 && chunk.t1 - last > 1.6) return null;
  return (
    <div
      style={{
        position: 'absolute',
        left: 60,
        right: 60,
        top: 1440,
        textAlign: 'center',
        fontFamily: F.sans,
        fontWeight: 800,
        fontSize: 60,
        letterSpacing: '-0.01em',
        lineHeight: 1.15,
      }}
    >
      <div style={{display: 'inline-block', background: 'rgba(250,249,245,0.95)', borderRadius: 26, padding: '12px 30px 16px', boxShadow: '0 10px 30px rgba(70,45,25,0.16)'}}>
      {chunk.words.map((w, i) => {
        const a = p(t, w.t - 0.02, 0.28, E.outCubic);
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              marginRight: i < chunk.words.length - 1 ? '0.27em' : 0,
              color: w.hi ? C.orange : C.ink,
              opacity: a,
              transform: `translateY(${(1 - a) * 16}px) scale(${0.94 + 0.06 * a})`,
            }}
          >
            {w.w}
          </span>
        );
      })}
      </div>
    </div>
  );
};
