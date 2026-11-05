import {Easing, spring, useCurrentFrame, useVideoConfig} from 'remotion';

export const clamp = (x: number, a = 0, b = 1) => Math.min(b, Math.max(a, x));
export const mix = (a: number, b: number, x: number) => a + (b - a) * x;

export const E = {
  outExpo: Easing.bezier(0.16, 1, 0.3, 1),
  outQuint: Easing.bezier(0.22, 1, 0.36, 1),
  outCubic: Easing.bezier(0.33, 1, 0.68, 1),
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  inOutSoft: Easing.bezier(0.45, 0, 0.2, 1),
  in: Easing.bezier(0.55, 0, 1, 0.45),
  inCubic: Easing.bezier(0.32, 0, 0.67, 0),
  outBack: Easing.bezier(0.34, 1.56, 0.64, 1),
  linear: (x: number) => x,
};

/** seconds since composition start */
export const useT = () => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  return {t: frame / fps, fps, frame};
};

/** eased progress 0..1 of a window [start, start+dur] */
export const p = (t: number, start: number, dur: number, e: (x: number) => number = E.outExpo) =>
  e(clamp((t - start) / dur));

export type SpringCfg = {damping?: number; stiffness?: number; mass?: number};
export const SPR = {
  soft: {damping: 18, stiffness: 120, mass: 0.9},
  pop: {damping: 11, stiffness: 170, mass: 0.7},
  snappy: {damping: 20, stiffness: 260, mass: 0.6},
  gentle: {damping: 26, stiffness: 90, mass: 1},
};

/** physical spring 0 -> 1 (may overshoot) starting at `start` seconds */
export const sp = (t: number, start: number, fps: number, cfg: SpringCfg = SPR.soft) =>
  t <= start ? 0 : spring({frame: (t - start) * fps, fps, config: cfg});

/** a standard enter / exit envelope */
export const env = (
  t: number,
  fps: number,
  tin: number,
  tout: number | null,
  opt: {cfg?: SpringCfg; outDur?: number} = {}
) => {
  const a = sp(t, tin, fps, opt.cfg ?? SPR.soft);
  const e = tout == null ? 0 : p(t, tout, opt.outDur ?? 0.45, E.inCubic);
  const vis = clamp(a * 1.6) * (1 - e);
  return {a, e, vis, on: t >= tin - 0.05 && (tout == null || t < tout + (opt.outDur ?? 0.45) + 0.05)};
};

/** keyframe track. frames: [time, value-object, easing-to-next?] */
export type KF<T> = [number, T, ((x: number) => number)?];
export function track<T extends Record<string, number>>(t: number, kfs: KF<T>[], defE = E.inOut): T {
  if (t <= kfs[0][0]) return kfs[0][1];
  for (let i = 0; i < kfs.length - 1; i++) {
    const [t0, v0, e0] = kfs[i];
    const [t1, v1] = kfs[i + 1];
    if (t < t1) {
      const x = (e0 ?? defE)(clamp((t - t0) / (t1 - t0)));
      const out: any = {};
      for (const k of Object.keys(v0)) out[k] = mix(v0[k], (v1 as any)[k], x);
      return out;
    }
  }
  return kfs[kfs.length - 1][1];
}

/** typed substring */
export const typed = (s: string, t: number, start: number, cps = 28) =>
  s.slice(0, Math.max(0, Math.floor((t - start) * cps)));

export const blink = (t: number, rate = 1.06) => (Math.floor(t * rate * 2) % 2 === 0 ? 1 : 0);

/** deterministic pseudo-random */
export const rnd = (i: number) => {
  const x = Math.sin(i * 127.1 + 311.7) * 43758.5453;
  return x - Math.floor(x);
};
