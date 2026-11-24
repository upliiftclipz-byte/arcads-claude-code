"""Synthesize an original background music bed for an ad (no samples, so no licensing questions).

Soft pad + plucked arpeggio + gentle kick/shaker over a I-V-vi-IV progression.
  --mood warm    100 BPM, C major (default; calm, trustworthy)
  --mood bright  118 BPM, D major, busier arpeggio (energetic)
  --mood calm     84 BPM, F major, no kick (premium, ASMR-ish)

Usage: .venv-chatterbox/bin/python skills/chatterbox-voiceover/scripts/make-music.py OUT.wav --seconds 24.3 [--mood warm] [--bpm N]
"""
import argparse
import numpy as np
import soundfile as sf

MOODS = {"warm": (100, 0, True, False), "bright": (118, 2, True, True), "calm": (84, 5, False, False)}
ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
ap.add_argument("out")
ap.add_argument("--seconds", type=float, required=True, help="Match the video length (ffprobe it)")
ap.add_argument("--mood", choices=MOODS, default="warm")
ap.add_argument("--bpm", type=float, help="Override the mood's tempo")
args = ap.parse_args()
bpm, TRANSPOSE, KICK, BUSY = MOODS[args.mood]

SR = 48000
BPM = args.bpm or bpm
BEAT = 60 / BPM
SECONDS = args.seconds
N = int(SR * SECONDS)
rng = np.random.default_rng(3)
t_all = np.arange(N) / SR


def note_hz(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def tone(freq, dur, harmonics=(1.0, 0.35, 0.15), detune=0.0):
    t = np.arange(int(SR * dur)) / SR
    out = np.zeros_like(t)
    for k, amp in enumerate(harmonics, start=1):
        out += amp * np.sin(2 * np.pi * freq * k * (1 + detune) * t)
    return out


def place(buf, sig, start_s, gain=1.0):
    i = int(start_s * SR)
    if i >= len(buf):
        return
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[: j - i]


# Chords as MIDI notes (C, G, Am, F), one bar (4 beats) each
CHORDS = [[n + TRANSPOSE for n in c] for c in
          [[48, 55, 60, 64, 67], [43, 55, 59, 62, 67], [45, 57, 60, 64, 69], [41, 53, 57, 60, 65]]]
BAR = 4 * BEAT

pad = np.zeros(N)
pluck = np.zeros(N)
drums = np.zeros(N)

bar = 0
while bar * BAR < SECONDS:
    chord = CHORDS[bar % 4]
    start = bar * BAR
    # Pad: detuned soft tones with slow attack/release, overlapping slightly
    dur = BAR + 0.4
    env = np.minimum(1, np.arange(int(SR * dur)) / (SR * 0.35))
    env *= np.minimum(1, (int(SR * dur) - np.arange(int(SR * dur))) / (SR * 0.5))
    for m in chord[1:]:
        for d in (-0.002, 0.002):
            place(pad, tone(note_hz(m), dur, (1.0, 0.2, 0.05), d) * env, start, 0.05)
    place(pad, tone(note_hz(chord[0] - 12), dur, (1.0, 0.3)) * env, start, 0.10)  # bass
    # Pluck arpeggio, eighth notes (sixteenths when busy)
    arp = [chord[1], chord[2], chord[3], chord[4], chord[3], chord[2], chord[3], chord[4]]
    step = BEAT / 4 if BUSY else BEAT / 2
    arp = arp * (2 if BUSY else 1)
    for k, m in enumerate(arp):
        d = 0.5
        e = np.exp(-np.arange(int(SR * d)) / (SR * 0.12))
        place(pluck, tone(note_hz(m + 12), d, (1.0, 0.5, 0.25, 0.1)) * e, start + k * step, 0.05 if BUSY else 0.06)
    # Kick on 1 and 3, shaker on off-beats
    for b in range(4):
        bt = start + b * BEAT
        if KICK and b in (0, 2):
            d = 0.25
            tt = np.arange(int(SR * d)) / SR
            f = 50 + 70 * np.exp(-tt * 30)
            kick = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 14)
            place(drums, kick, bt, 0.35)
        d = 0.06
        sh = rng.standard_normal(int(SR * d)) * np.exp(-np.arange(int(SR * d)) / (SR * 0.015))
        sh = np.diff(sh, prepend=0)  # crude high-pass
        place(drums, sh, bt + BEAT / 2, 0.05)
    bar += 1

mix = pad + pluck + drums
# Fade in 0.6s, fade out 1.5s
fade_in = np.minimum(1, t_all / 0.6)
fade_out = np.minimum(1, (SECONDS - t_all) / 1.5)
mix *= fade_in * np.clip(fade_out, 0, 1)
mix /= np.max(np.abs(mix)) + 1e-9
mix *= 0.8
stereo = np.stack([mix, np.roll(mix, int(SR * 0.008))], axis=1)  # tiny width
sf.write(args.out, stereo, SR)
print(f"Wrote {args.out} ({SECONDS:.1f}s, {BPM:g} BPM, {args.mood})")
