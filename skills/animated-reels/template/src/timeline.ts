/**
 * THE SCRIPT. Every scene keys off these beats, so re-timing the whole video to
 * Darius's real voiceover = replacing the durations (or word times) here.
 * Syntax: "|" breaks a caption chunk, *word* is an orange accent.
 */
import {VO} from './voTiming';

export type Beat = {id: string; d: number; text: string};

export const BEATS: Beat[] = [
  // EDIT THESE. One beat = one spoken sentence. d = seconds (ignored once a voiceover is synced).
  {id: 'hook', d: 2.6, text: 'This reel | was written as *code.*'},
  {id: 'code', d: 3.2, text: 'Every frame | is a *React* component, | rendered by *Remotion.*'},
  {id: 'stat', d: 2.6, text: 'No editor. | No *credits.* | No timeline.'},
  {id: 'cta', d: 2.4, text: 'Comment *WORD,* | and I\'ll send you | the *link.*'},
  {id: 'save', d: 2.0, text: '*Save* this | so you can | come back to it.'},
];

export const TAIL = 0.5;

/** minimum on-screen time per beat when a voiceover drives the pacing (animations need room) */
const FLOOR: Record<string, number> = {save: 2.4};

/** with a voiceover: each beat lasts as long as its slice of the VO (or its floor), and the
 *  slice [voStart, voEnd) of vo.mp3 is played from the beat's start */
export const VO_SLICES: {id: string; at: number; from: number; to: number}[] = [];
if (VO) {
  BEATS.forEach((b, i) => {
    const cut = (k: number) => (VO.beats[k] as any).cut ?? Math.max(0, VO.beats[k].start - 0.06);
    const from = i === 0 ? 0 : cut(i);
    const to = i + 1 < VO.beats.length ? Math.max(from, cut(i + 1)) : VO.total;
    b.d = Math.max(to - from, FLOOR[b.id] ?? 0);
    VO_SLICES.push({id: b.id, at: 0, from, to});
  });
}

export const T: Record<string, number> = {};
{
  let acc = 0;
  for (const b of BEATS) {
    T[b.id] = acc;
    acc += b.d;
  }
  T.end = acc;
  VO_SLICES.forEach((x) => (x.at = T[x.id]));
}
export const DURATION = T.end + TAIL;
export const dur = (id: string) => BEATS.find((b) => b.id === id)!.d;

// ---------- caption words ----------
export type Word = {w: string; hi: boolean; t: number; chunk: number};
export type Chunk = {i: number; words: Word[]; t0: number; t1: number};

const clean = (w: string) => w.replace(/\*/g, '');

export const CHUNKS: Chunk[] = (() => {
  const chunks: Chunk[] = [];
  BEATS.forEach((b, bi) => {
    const parts = b.text.split('|').map((s) => s.trim()).filter(Boolean);
    // words with accent flags (an accent may span words: *Claude Code*)
    const flat: {w: string; hi: boolean; c: number}[] = [];
    parts.forEach((part, pi) => {
      let inHi = false;
      for (const raw of part.split(/\s+/)) {
        const starts = raw.startsWith('*');
        const ends = raw.replace(/[.,?!]+$/, '').endsWith('*');
        if (starts) inHi = true;
        flat.push({w: clean(raw), hi: inHi, c: pi});
        if (ends) inHi = false;
      }
    });
    const chars = flat.reduce((a, x) => a + x.w.length, 0);
    const speech = Math.min(b.d - 0.15, 0.052 * chars + 0.1 * flat.length);
    const t0 = T[b.id] + 0.04;
    let acc = 0;
    const voWords = VO ? VO.words.filter((w) => w.beat === bi) : null;
    const slice = VO ? VO_SLICES[bi] : null;
    const words: Word[] = flat.map((x, k) => {
      let wt = t0 + (acc / (0.052 * chars + 0.1 * flat.length)) * speech;
      if (voWords && slice && voWords[k]) wt = Math.max(T[b.id], T[b.id] + (voWords[k].start - slice.from) - 0.15);  // v4 alignment runs ~0.1-0.2 s late
      acc += 0.052 * x.w.length + 0.1;
      return {w: x.w, hi: x.hi, t: wt, chunk: x.c};
    });
    parts.forEach((_, pi) => {
      const ws = words.filter((w) => w.chunk === pi);
      chunks.push({i: chunks.length, words: ws, t0: ws[0].t, t1: 0});
    });
  });
  for (let i = 0; i < chunks.length; i++) {
    chunks[i].t1 = i + 1 < chunks.length ? chunks[i + 1].t0 : DURATION;
  }
  return chunks;
})();

/** time of the first caption word matching `w` at/after time `after` */
export const wordAt = (w: string, after = 0) => {
  for (const c of CHUNKS) for (const x of c.words) if (x.t >= after - 0.001 && x.w.toLowerCase().replace(/[^a-z0-9']/g, '') === w.toLowerCase()) return x.t;
  return after;
};
