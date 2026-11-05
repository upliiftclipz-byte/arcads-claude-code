// A working example reel. Copy the patterns, then replace the scenes with your own.
// Every scene reads its timing from T.<beatId> and wordAt('word', T.<beatId>), so when the
// voiceover changes, everything re-times itself.
import React from 'react';
import {AbsoluteFill} from 'remotion';
import {C, F, SHADOW} from '../theme';
import {T, wordAt} from '../timeline';
import {blink, clamp, E, mix, p, sp, SPR, typed, useT} from '../anim';
import {ClaudeMark, Pop, RollText} from '../components/primitives';

const GREEN = '#2F9E5B';

/** a scene that swings in and out in 3D */
const Swing: React.FC<{tin: number; tout: number; children: React.ReactNode}> = ({tin, tout, children}) => {
  const {t, fps} = useT();
  if (t < tin - 0.05 || t > tout + 0.5) return null;
  const a = sp(t, tin, fps, {damping: 20, stiffness: 140, mass: 0.9});
  const e = p(t, tout, 0.42, E.inCubic);
  const bl = (1 - clamp(a)) * 14 + e * 16;
  return (
    <AbsoluteFill style={{perspective: 1800}}>
      <AbsoluteFill
        style={{
          transform: `translateX(${(1 - a) * 240 - e * 300}px) rotateY(${(1 - a) * 34 - e * 40}deg) scale(${mix(0.9, 1, a) * mix(1, 0.92, e)})`,
          opacity: clamp(a * 1.8) * (1 - e),
          filter: bl > 0.2 ? `blur(${bl}px)` : undefined,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** a desktop window */
const Win: React.FC<{title: string; top: number; h: number; children: React.ReactNode}> = ({title, top, h, children}) => (
  <div style={{position: 'absolute', left: 90, top, width: 900, height: h, borderRadius: 30, background: '#fff', border: '1px solid rgba(20,20,19,0.08)', boxShadow: SHADOW.lg, overflow: 'hidden'}}>
    <div style={{height: 64, background: 'linear-gradient(#FBFAF7, #F5F3EE)', borderBottom: `1px solid ${C.line}`, position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10}}>
      <div style={{position: 'absolute', left: 26, top: 23, display: 'flex', gap: 10}}>
        {['#FF5F57', '#FEBC2E', '#28C840'].map((c) => (
          <div key={c} style={{width: 18, height: 18, borderRadius: 9, background: c}} />
        ))}
      </div>
      <ClaudeMark size={22} />
      <div style={{fontFamily: F.sans, fontWeight: 600, fontSize: 23, color: '#8E8B82'}}>{title}</div>
    </div>
    <div style={{position: 'absolute', top: 64, left: 0, right: 0, bottom: 0, padding: '34px 40px'}}>{children}</div>
  </div>
);

const Pill: React.FC<{children: React.ReactNode; tone?: 'white' | 'orange'; size?: number}> = ({children, tone = 'white', size = 34}) => (
  <div
    style={{
      display: 'inline-flex', alignItems: 'center', gap: size * 0.4, padding: `${size * 0.4}px ${size * 0.7}px`, borderRadius: 999,
      fontFamily: F.sans, fontWeight: 700, fontSize: size, whiteSpace: 'nowrap',
      ...(tone === 'orange' ? {background: C.orange, color: '#fff', boxShadow: '0 10px 30px rgba(217,119,87,0.4)'} : {background: '#fff', color: C.ink, boxShadow: SHADOW.md, border: `1px solid ${C.line}`}),
    }}
  >
    {children}
  </div>
);

// ---------- 1. headline that rolls in, word by word
const Hook: React.FC = () => {
  const {t} = useT();
  const tout = T.code - 0.1;
  if (t > tout + 0.8) return null;
  return <RollText lines={['This reel was', 'written as *code*']} text="" tin={-0.6} tout={tout} size={124} align="center" stagger={0.1} style={{position: 'absolute', left: 0, right: 0, top: 640}} />;
};

// ---------- 2. code typing inside a window
const CODE = ['<Reel style="any">', '  <Hook text={idea} />', '  <Scene kind="proof" />', '  <Captions words={voice} />', '</Reel>'];
const Code: React.FC = () => {
  const {t} = useT();
  let budget = Math.max(0, Math.floor((t - T.code - 0.3) * 38));
  return (
    <Swing tin={T.code - 0.05} tout={T.stat - 0.15}>
      <Win title="Claude · reel.tsx" top={420} h={600}>
        <div style={{fontFamily: F.mono, fontSize: 40, lineHeight: 1.55, whiteSpace: 'pre', color: C.ink2}}>
          {CODE.map((line, i) => {
            const n = Math.min(line.length, budget);
            budget -= n;
            return (
              <div key={i}>
                {n > 0 ? line.slice(0, n) : ' '}
                {n > 0 && n < line.length ? <span style={{display: 'inline-block', width: 4, height: 44, background: C.orange, verticalAlign: 'middle', opacity: blink(t)}} /> : null}
              </div>
            );
          })}
        </div>
      </Win>
    </Swing>
  );
};

// ---------- 3. chips that pop on the spoken word
const Stat: React.FC = () => {
  const {t} = useT();
  if (t < T.stat - 0.1 || t > T.cta + 0.6) return null;
  const e = p(t, T.cta - 0.15, 0.4, E.inCubic);
  return (
    <AbsoluteFill style={{opacity: 1 - e}}>
      {['editor', 'credits', 'timeline'].map((w, i) => (
        <Pop key={w} tin={wordAt(w, T.stat) - 0.1} x={0} y={620 + i * 140} style={{width: 1080, display: 'flex', justifyContent: 'center'}}>
          <Pill size={48}>no {w}</Pill>
        </Pop>
      ))}
    </AbsoluteFill>
  );
};

// ---------- 4. comment box that types the keyword, then the save chip
const Cta: React.FC = () => {
  const {t, fps} = useT();
  if (t < T.cta - 0.1) return null;
  const a = sp(t, T.cta, fps, SPR.pop);
  const tKey = wordAt('word', T.cta) - 0.05;
  const posted = t > tKey + 0.5;
  const sv = sp(t, wordAt('save', T.save) - 0.1, fps, SPR.pop);
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 0, right: 0, top: 450, display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 16, transform: `scale(${a})`}}>
        <ClaudeMark size={64} />
        <div style={{fontFamily: F.serif, fontSize: 110, color: C.ink}}>Comment</div>
      </div>
      <div style={{position: 'absolute', left: 90, right: 90, top: 630, height: 130, borderRadius: 30, background: '#fff', border: `2px solid ${C.line2}`, boxShadow: SHADOW.md, display: 'flex', alignItems: 'center', padding: '0 34px', transform: `scale(${a})`}}>
        <div style={{fontFamily: F.sans, fontWeight: 900, fontSize: 70, color: C.ink}}>{typed('WORD', t, tKey, 16)}</div>
        <div style={{marginLeft: 'auto', fontFamily: F.sans, fontWeight: 800, fontSize: 38, color: posted ? GREEN : C.orange}}>{posted ? 'Posted ✓' : 'Post'}</div>
      </div>
      {sv > 0 ? (
        <div style={{position: 'absolute', left: 0, right: 0, top: 860, display: 'flex', justifyContent: 'center', transform: `scale(${sv})`}}>
          <Pill size={42}>Save this</Pill>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};

export const ExampleReel: React.FC = () => (
  <>
    <Hook />
    <Code />
    <Stat />
    <Cta />
  </>
);
