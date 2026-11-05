import React from 'react';
import {AbsoluteFill, spring} from 'remotion';
import {C, F, SHADOW} from '../theme';
import {CLAUDE_PATH, INSTAGRAM_PATH, OPENAI_PATH, TIKTOK_PATH, YOUTUBE_PATH} from '../logoPaths';
import {clamp, E, mix, p, rnd, useT} from '../anim';

// ---------------- Background ----------------
export const Background: React.FC = () => {
  const {t} = useT();
  const b1x = 30 + Math.sin(t * 0.21) * 10;
  const b1y = 22 + Math.cos(t * 0.17) * 6;
  const b2x = 75 + Math.cos(t * 0.19) * 10;
  const b2y = 78 + Math.sin(t * 0.23) * 6;
  return (
    <AbsoluteFill style={{background: C.bg}}>
      <AbsoluteFill
        style={{
          background: `radial-gradient(circle at ${b1x}% ${b1y}%, rgba(217,119,87,0.10) 0%, rgba(217,119,87,0) 42%),
            radial-gradient(circle at ${b2x}% ${b2y}%, rgba(214,170,130,0.20) 0%, rgba(214,170,130,0) 46%),
            radial-gradient(ellipse at 50% 45%, rgba(255,255,255,0.65) 0%, rgba(255,255,255,0) 60%)`,
        }}
      />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, rgba(0,0,0,0) 62%, rgba(110,80,50,0.07) 100%)'}} />
      <svg width="100%" height="100%" style={{position: 'absolute', inset: 0, opacity: 0.07, mixBlendMode: 'multiply'}}>
        <filter id="grain">
          <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" stitchTiles="stitch" />
          <feColorMatrix type="saturate" values="0" />
        </filter>
        <rect width="100%" height="100%" filter="url(#grain)" />
      </svg>
    </AbsoluteFill>
  );
};

// ---------------- Logos ----------------
export const ClaudeMark: React.FC<{size: number; color?: string; style?: React.CSSProperties}> = ({size, color = C.orange, style}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={style}>
    <path d={CLAUDE_PATH} fill={color} />
  </svg>
);

export const OpenAIMark: React.FC<{size: number; color?: string}> = ({size, color = C.ink}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path d={OPENAI_PATH} fill={color} />
  </svg>
);

export const InstagramMark: React.FC<{size: number; mono?: string}> = ({size, mono}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <defs>
      <radialGradient id={`ig${size}`} cx="30%" cy="107%" r="150%">
        <stop offset="0%" stopColor="#FDF497" />
        <stop offset="5%" stopColor="#FDF497" />
        <stop offset="45%" stopColor="#FD5949" />
        <stop offset="60%" stopColor="#D6249F" />
        <stop offset="90%" stopColor="#285AEB" />
      </radialGradient>
    </defs>
    <path d={INSTAGRAM_PATH} fill={mono ?? `url(#ig${size})`} />
  </svg>
);

export const TikTokMark: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 24 24" style={{overflow: 'visible'}}>
    <path d={TIKTOK_PATH} fill="#25F4EE" transform="translate(-0.6,-0.5)" />
    <path d={TIKTOK_PATH} fill="#FE2C55" transform="translate(0.6,0.5)" />
    <path d={TIKTOK_PATH} fill="#111" />
  </svg>
);

export const YouTubeMark: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <rect x="7" y="7" width="11" height="10" fill="#fff" />
    <path d={YOUTUBE_PATH} fill="#FF0033" />
  </svg>
);

// ---------------- Small UI atoms ----------------
export const Check: React.FC<{size: number; color?: string; bg?: string; draw?: number}> = ({size, color = '#fff', bg = C.orange, draw = 1}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="12" fill={bg} />
    <path
      d="M6.8 12.4 L10.3 15.8 L17.4 8.6"
      fill="none"
      stroke={color}
      strokeWidth="2.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeDasharray="16"
      strokeDashoffset={16 * (1 - draw)}
    />
  </svg>
);

export const Cross: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <circle cx="12" cy="12" r="12" fill={C.red} />
    <path d="M8 8 L16 16 M16 8 L8 16" stroke="#fff" strokeWidth="2.6" strokeLinecap="round" />
  </svg>
);

export const Chip: React.FC<{
  children: React.ReactNode;
  style?: React.CSSProperties;
  tone?: 'white' | 'orange' | 'soft' | 'ink';
  size?: number;
}> = ({children, style, tone = 'white', size = 30}) => {
  const tones: Record<string, React.CSSProperties> = {
    white: {background: '#fff', color: C.ink, boxShadow: SHADOW.sm, border: `1px solid ${C.line}`},
    orange: {background: C.orange, color: '#fff', boxShadow: '0 8px 24px rgba(217,119,87,0.35)'},
    soft: {background: C.orangeTint, color: C.orangeDeep, border: `1px solid ${C.orangeSoft}`},
    ink: {background: C.ink, color: '#fff'},
  };
  return (
    <div
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: size * 0.4,
        padding: `${size * 0.42}px ${size * 0.7}px`,
        borderRadius: 999,
        fontFamily: F.sans,
        fontWeight: 700,
        fontSize: size,
        whiteSpace: 'nowrap',
        ...tones[tone],
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** generic enter/exit wrapper: spring in from below with blur, ease out upward */
export const Pop: React.FC<{
  tin: number;
  tout?: number | null;
  children: React.ReactNode;
  x?: number;
  y?: number;
  from?: {y?: number; s?: number; blur?: number; r?: number; x?: number};
  to?: {y?: number; s?: number; blur?: number; x?: number};
  cfg?: {damping?: number; stiffness?: number; mass?: number};
  outDur?: number;
  style?: React.CSSProperties;
  origin?: string;
}> = ({tin, tout = null, children, x, y, from = {}, to = {}, cfg, outDur = 0.4, style, origin}) => {
  const {t, fps} = useT();
  if (t < tin - 0.02) return null;
  if (tout != null && t > tout + outDur + 0.02) return null;
  const a = t <= tin ? 0 : spring({frame: (t - tin) * fps, fps, config: cfg ?? {damping: 16, stiffness: 140, mass: 0.8}});
  const e = tout == null ? 0 : p(t, tout, outDur, E.inCubic);
  const fy = from.y ?? 40;
  const fs = from.s ?? 0.92;
  const fb = from.blur ?? 10;
  const fr = from.r ?? 0;
  const fx = from.x ?? 0;
  const ty = to.y ?? -24;
  const ts = to.s ?? 0.97;
  const tb = to.blur ?? 8;
  const tx = to.x ?? 0;
  const ty2 = mix(fy, 0, a) + ty * e;
  const tx2 = mix(fx, 0, a) + tx * e;
  const sc = mix(fs, 1, a) * mix(1, ts, e);
  const bl = Math.max(0, fb * (1 - clamp(a)) + tb * e);
  const op = clamp(a * 1.8) * (1 - e);
  return (
    <div
      style={{
        position: x != null || y != null ? 'absolute' : undefined,
        left: x,
        top: y,
        transform: `translate(${tx2}px, ${ty2}px) scale(${sc}) rotate(${fr * (1 - a)}deg)`,
        transformOrigin: origin ?? 'center',
        filter: bl > 0.05 ? `blur(${bl}px)` : undefined,
        opacity: op,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** radial spark burst (Claude-spark confetti) */
export const Burst: React.FC<{t0: number; x: number; y: number; n?: number; r?: number; color?: string; size?: number}> = ({
  t0,
  x,
  y,
  n = 10,
  r = 160,
  color = C.orange,
  size = 26,
}) => {
  const {t} = useT();
  const k = (t - t0) / 0.9;
  if (k < 0 || k > 1) return null;
  const pr = E.outExpo(k);
  return (
    <div style={{position: 'absolute', left: x, top: y, width: 0, height: 0, pointerEvents: 'none'}}>
      {Array.from({length: n}).map((_, i) => {
        const ang = (i / n) * Math.PI * 2 + rnd(i) * 0.5;
        const rr = r * (0.6 + rnd(i + 9) * 0.5) * pr;
        const s = size * (0.5 + rnd(i + 3) * 0.6) * (1 - k * 0.6);
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: Math.cos(ang) * rr - s / 2,
              top: Math.sin(ang) * rr - s / 2,
              opacity: 1 - k,
              transform: `rotate(${k * 160 + i * 30}deg)`,
            }}
          >
            {i % 3 === 0 ? (
              <ClaudeMark size={s} color={color} />
            ) : (
              <div style={{width: s * 0.38, height: s * 0.38, borderRadius: 99, background: color}} />
            )}
          </div>
        );
      })}
    </div>
  );
};

/** words that rise out of a mask. text: words with *accent* (italic orange) */
export const RollText: React.FC<{
  text: string;
  tin: number;
  tout?: number | null;
  size: number;
  font?: string;
  weight?: number;
  color?: string;
  accent?: string;
  stagger?: number;
  inDur?: number;
  italicAccent?: boolean;
  align?: 'left' | 'center';
  lineHeight?: number;
  letterSpacing?: string;
  upper?: boolean;
  style?: React.CSSProperties;
  lines?: string[]; // optional explicit line breaks (each a text)
  lineStyle?: (li: number) => React.CSSProperties;
  outDur?: number;
  outStagger?: number;
}> = (props) => {
  const {t} = useT();
  const {
    text,
    tin,
    tout = null,
    size,
    font = F.serif,
    weight = 400,
    color = C.ink,
    accent = C.orange,
    stagger = 0.045,
    inDur = 0.75,
    italicAccent = true,
    align = 'left',
    lineHeight = 1.04,
    letterSpacing,
    upper,
    style,
  } = props;
  if (t < tin - 0.02) return null;
  if (tout != null && t > tout + 0.8) return null;
  const lines = props.lines ?? [text];
  let wi = 0;
  return (
    <div style={{textAlign: align, ...style}}>
      {lines.map((ln, li) => {
        let inHi = false;
        const words = ln.split(' ').map((raw) => {
          const starts = raw.startsWith('*');
          if (starts) inHi = true;
          const w = {w: raw.replace(/\*/g, ''), hi: inHi};
          if (raw.replace(/[.,?!]+$/, '').endsWith('*')) inHi = false;
          return w;
        });
        return (
          <div key={li} style={{display: 'block', whiteSpace: 'nowrap', lineHeight, ...(props.lineStyle ? props.lineStyle(li) : {})}}>
            {words.map((w, i) => {
              const idx = wi++;
              const a = p(t, tin + idx * stagger, inDur, E.outExpo);
              const e = tout == null ? 0 : p(t, tout + idx * (props.outStagger ?? 0.025), props.outDur ?? 0.42, E.inCubic);
              const y = (1 - a) * 115 - e * 115;
              const bl = (1 - a) * 6 + e * 6;
              const it = w.hi && italicAccent && font === F.serif;
              return (
                <span
                  key={i}
                  style={{
                    display: 'inline-block',
                    overflow: 'hidden',
                    verticalAlign: 'top',
                    padding: `0.04em ${it ? 0.08 : 0.02}em 0.16em 0.02em`,
                    margin: `-0.04em ${it ? -0.08 : -0.02}em -0.16em -0.02em`,
                  }}
                >
                  <span
                    style={{
                      display: 'inline-block',
                      transform: `translateY(${y}%)`,
                      filter: bl > 0.1 ? `blur(${bl}px)` : undefined,
                      fontFamily: font,
                      fontWeight: weight,
                      fontSize: size,
                      fontStyle: it ? 'italic' : 'normal',
                      color: w.hi ? accent : color,
                      letterSpacing,
                      textTransform: upper ? 'uppercase' : undefined,
                    }}
                  >
                    {w.w}
                  </span>
                  {i < words.length - 1 ? <span style={{display: 'inline-block', width: size * (font === F.serif ? 0.22 : 0.28)}} /> : null}
                </span>
              );
            })}
          </div>
        );
      })}
    </div>
  );
};

/** generic white card */
export const Card: React.FC<{w: number; h?: number; r?: number; style?: React.CSSProperties; children?: React.ReactNode}> = ({
  w,
  h,
  r = 26,
  style,
  children,
}) => (
  <div
    style={{
      width: w,
      height: h,
      borderRadius: r,
      background: C.card,
      border: `1px solid rgba(20,20,19,0.07)`,
      boxShadow: SHADOW.md,
      overflow: 'hidden',
      position: 'relative',
      ...style,
    }}
  >
    {children}
  </div>
);
