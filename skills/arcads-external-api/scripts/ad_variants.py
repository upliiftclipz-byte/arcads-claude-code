#!/usr/bin/env python3
"""Ad variations toolkit: hook swaps + aspect-ratio versions, all local with ffmpeg (no credits).

Python 3.9+ standard library and ffmpeg/ffprobe on PATH (override with FFMPEG / FFPROBE).

Commands (run from the repo root):

  probe        Duration, resolution, fps and audio of a video
  suggest-cut  Candidate end points of the original hook (scene changes + pauses in speech)
  frame        Save one frame as JPG (e.g. the body's first frame, as a startFrame for a new hook)
  trim         Cut a clip to a time range (generated hooks often run longer than the line)
  splice       Replace the first N seconds of an ad with a new hook clip
  reframe      Make 9:16 / 1:1 / 4:5 / 16:9 versions (blur-fill, crop or pad)
  matrix       hooks x ratios in one go, plus manifest.csv / manifest.json for upload and testing

Examples:

  S=skills/arcads-external-api/scripts/ad_variants.py
  python3 $S suggest-cut outputs/ad/approved.mp4
  python3 $S frame outputs/ad/approved.mp4 --at 3.2 --out outputs/ad/body-start.jpg
  python3 $S splice --hook outputs/ad/hook-b.mp4 --body outputs/ad/approved.mp4 --cut 3.2 --out outputs/ad/v-b.mp4
  python3 $S reframe outputs/ad/approved.mp4 --ratios 9:16,1:1,4:5,16:9 --mode blur --out outputs/ad/ratios
  python3 $S matrix --body outputs/ad/approved.mp4 --cut 3.2 --hooks outputs/ad/hook-*.mp4 \
      --include-original --ratios 9:16,1:1,16:9 --name sunscreen-ugc --out outputs/ad-variations/2026-11-21
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

FFMPEG = os.environ.get("FFMPEG", "ffmpeg")
FFPROBE = os.environ.get("FFPROBE", "ffprobe")

# Output canvases (width, height). 1080 on the short side is what Meta/TikTok/YouTube expect.
CANVAS = {"9:16": (1080, 1920), "1:1": (1080, 1080), "4:5": (1080, 1350), "16:9": (1920, 1080)}
PLACEMENTS = {
    "9:16": "TikTok, Reels, Shorts, Stories",
    "1:1": "Feed (Meta, LinkedIn), carousels",
    "4:5": "Meta/Instagram feed (tallest feed format)",
    "16:9": "YouTube in-stream, landscape placements",
}


# ── helpers ─────────────────────────────────────────────────────────────────
def need_tools():
    for t in (FFMPEG, FFPROBE):
        if not shutil.which(t):
            sys.exit(f"{t} not found. Install ffmpeg (macOS: brew install ffmpeg; Linux: apt-get install ffmpeg).")


def run(cmd: list[str]):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        sys.exit(f"ffmpeg failed:\n{' '.join(cmd)}\n{r.stderr[-1500:]}")
    return r


def probe(path: Path) -> dict:
    if not path.is_file():
        sys.exit(f"Not found: {path}")
    out = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries",
         "format=duration:stream=index,codec_type,width,height,r_frame_rate,sample_rate,channels",
         "-of", "json", str(path)], capture_output=True, text=True)
    if out.returncode != 0:
        sys.exit(f"Can't read {path}: {out.stderr.strip()}")
    d = json.loads(out.stdout)
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), None)
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    if not v:
        sys.exit(f"No video stream in {path}")
    num, _, den = v.get("r_frame_rate", "30/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 30.0
    return {
        "path": str(path), "duration": float(d.get("format", {}).get("duration", 0) or 0),
        "width": int(v["width"]), "height": int(v["height"]), "fps": round(fps, 3),
        "audio": bool(a), "sample_rate": int(a["sample_rate"]) if a and a.get("sample_rate") else None,
    }


def ratio_label(w: int, h: int) -> str:
    r = w / h
    best = min(CANVAS, key=lambda k: abs(CANVAS[k][0] / CANVAS[k][1] - r))
    return best if abs(CANVAS[best][0] / CANVAS[best][1] - r) < 0.02 else f"{w}x{h}"


def parse_ratios(s: str) -> list[str]:
    rs = [x.strip() for x in s.split(",") if x.strip()]
    bad = [x for x in rs if x not in CANVAS]
    if bad:
        sys.exit(f"Unknown ratio(s) {bad}. Use any of: {', '.join(CANVAS)}")
    return rs


def fit_filter(w: int, h: int, mode: str, focus_x: float = 0.5, focus_y: float = 0.5) -> str:
    """Video filter that maps any input onto a w x h canvas."""
    if mode == "crop":
        return (f"scale={w}:{h}:force_original_aspect_ratio=increase,"
                f"crop={w}:{h}:(iw-{w})*{focus_x}:(ih-{h})*{focus_y},setsar=1")
    if mode == "pad":
        return (f"scale={w}:{h}:force_original_aspect_ratio=decrease,"
                f"pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,setsar=1")
    # blur: the same footage, zoomed and blurred, fills the empty bands
    return (f"split=2[bg][fg];[bg]scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},"
            f"boxblur=luma_radius=40:luma_power=2,eq=brightness=-0.06[bgb];"
            f"[fg]scale={w}:{h}:force_original_aspect_ratio=decrease[fgs];"
            f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1")


ENC = ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
       "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart"]


# ── commands ────────────────────────────────────────────────────────────────
def cmd_probe(a):
    for p in a.videos:
        info = probe(Path(p))
        info["ratio"] = ratio_label(info["width"], info["height"])
        print(json.dumps(info))


def cmd_suggest_cut(a):
    info = probe(Path(a.video))
    limit = min(a.max, info["duration"])
    scenes = []
    r = subprocess.run([FFMPEG, "-hide_banner", "-t", str(limit), "-i", a.video, "-vf",
                        f"select='gt(scene,{a.threshold})',showinfo", "-an", "-f", "null", "-"],
                       capture_output=True, text=True)
    for m in re.finditer(r"pts_time:([0-9.]+)", r.stderr):
        t = float(m.group(1))
        if t >= 0.8:
            scenes.append(round(t, 2))
    pauses = []
    if info["audio"]:
        r = subprocess.run([FFMPEG, "-hide_banner", "-t", str(limit), "-i", a.video, "-af",
                            "silencedetect=n=-35dB:d=0.25", "-vn", "-f", "null", "-"], capture_output=True, text=True)
        starts = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", r.stderr)]
        ends = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", r.stderr)]
        for s, e in zip(starts, ends + [limit] * (len(starts) - len(ends))):
            mid = round((s + e) / 2, 2)
            if mid >= 0.8:
                pauses.append(mid)
    print(json.dumps({"video": a.video, "searched_first_seconds": round(limit, 2),
                      "scene_changes": scenes, "speech_pauses": pauses,
                      "hint": "Cut where the hook's last line ends: prefer a speech pause, ideally next to a scene change. "
                              "Confirm by watching, and by the transcript if the ad has dialogue."}, indent=2))


def cmd_frame(a):
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    run([FFMPEG, "-y", "-loglevel", "error", "-ss", str(a.at), "-i", a.video, "-frames:v", "1", "-q:v", "2", str(out)])
    print(f"Wrote {out}")


def cmd_trim(a):
    info = probe(Path(a.video))
    end = a.end if a.end is not None else info["duration"]
    if not 0 <= a.start < end <= info["duration"] + 0.05:
        sys.exit(f"Invalid range {a.start}-{end}s for a {info['duration']:.2f}s clip")
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    fade = []
    if info["audio"] and a.fade > 0:  # short audio fade-out avoids a click at the join
        fade = ["-af", f"afade=t=out:st={max(0.0, end - a.start - a.fade):.3f}:d={a.fade}"]
    run([FFMPEG, "-y", "-loglevel", "error", "-ss", str(a.start), "-to", str(end), "-i", a.video,
         *fade, *ENC, str(out)])
    print(json.dumps({"out": str(out), "duration": round(probe(out)["duration"], 2)}, indent=2))


def splice(hook: Path, body: Path, cut: float, out: Path, tail: float | None = None) -> dict:
    hb, bb = probe(hook), probe(body)
    if cut >= bb["duration"]:
        sys.exit(f"--cut {cut}s is beyond the body's length ({bb['duration']:.2f}s)")
    w, h, fps = bb["width"], bb["height"], bb["fps"] or 30
    norm = (f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"setsar=1,fps={fps},format=yuv420p")
    inputs = ["-i", str(hook), "-ss", str(cut)]
    if tail:
        inputs += ["-t", str(tail)]
    inputs += ["-i", str(body)]
    graph = [f"[0:v]{norm},setpts=PTS-STARTPTS[v0]", f"[1:v]{norm},setpts=PTS-STARTPTS[v1]"]
    extra = []
    # Audio: keep each clip's track; give silent clips a silent track so concat lines up.
    for i, info in enumerate((hb, bb)):
        if info["audio"]:
            graph.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS[a{i}]")
        else:
            idx = 2 + len(extra) // 6  # each silent source adds 6 args: -f lavfi -t D -i SRC
            dur = info["duration"] if i == 0 else max(0.01, (tail or bb["duration"] - cut))
            extra += ["-f", "lavfi", "-t", f"{dur:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
            graph.append(f"[{idx}:a]asetpts=PTS-STARTPTS[a{i}]")
    graph.append("[v0][a0][v1][a1]concat=n=2:v=1:a=1[v][a]")
    out.parent.mkdir(parents=True, exist_ok=True)
    run([FFMPEG, "-y", "-loglevel", "error", *inputs, *extra, "-filter_complex", ";".join(graph),
         "-map", "[v]", "-map", "[a]", *ENC, str(out)])
    res = probe(out)
    return {"out": str(out), "hook_seconds": round(hb["duration"], 2), "body_from": cut,
            "duration": round(res["duration"], 2), "size": f"{res['width']}x{res['height']}"}


def cmd_splice(a):
    need_tools()
    print(json.dumps(splice(Path(a.hook), Path(a.body), a.cut, Path(a.out)), indent=2))


def reframe(video: Path, ratio: str, mode: str, out: Path, focus_x: float, focus_y: float) -> dict:
    info = probe(video)
    w, h = CANVAS[ratio]
    same = abs(info["width"] / info["height"] - w / h) < 0.01
    vf = f"scale={w}:{h},setsar=1" if same else fit_filter(w, h, mode, focus_x, focus_y)
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [FFMPEG, "-y", "-loglevel", "error", "-i", str(video)]
    if ";" in vf or "[" in vf:
        cmd += ["-filter_complex", f"[0:v]{vf}[v]", "-map", "[v]", "-map", "0:a?"]
    else:
        cmd += ["-vf", vf, "-map", "0:v", "-map", "0:a?"]
    run(cmd + ENC + [str(out)])
    return {"out": str(out), "ratio": ratio, "size": f"{w}x{h}", "mode": "native" if same else mode,
            "placements": PLACEMENTS[ratio]}


def cmd_reframe(a):
    need_tools()
    src = Path(a.video)
    out_dir = Path(a.out)
    stem = a.name or src.stem
    results = [reframe(src, r, a.mode, out_dir / f"{stem}_{r.replace(':', 'x')}.mp4", a.focus_x, a.focus_y)
               for r in parse_ratios(a.ratios)]
    print(json.dumps(results, indent=2))


def cmd_matrix(a):
    need_tools()
    body, out_dir = Path(a.body), Path(a.out)
    ratios = parse_ratios(a.ratios)
    name = a.name or body.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    hooks: list[tuple[str, Path | None]] = []
    if a.include_original:
        hooks.append(("h0-original", None))
    for i, hp in enumerate(a.hooks or [], start=1):
        label = re.sub(r"[^a-z0-9-]+", "-", Path(hp).stem.lower()).strip("-")[:24]
        hooks.append((f"h{i}-{label}", Path(hp)))
    if not hooks:
        sys.exit("Nothing to do: pass --hooks and/or --include-original.")
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for hid, hp in hooks:
            if hp is None:
                master = body
            else:
                master = Path(tmp) / f"{hid}.mp4"
                splice(hp, body, a.cut, master)
            for r in ratios:
                fname = f"{name}_{hid}_{r.replace(':', 'x')}.mp4"
                res = reframe(master, r, a.mode, out_dir / fname, a.focus_x, a.focus_y)
                info = probe(out_dir / fname)
                rows.append({"file": fname, "variant_id": f"{name}_{hid}_{r.replace(':', 'x')}", "hook": hid,
                             "hook_source": str(hp) if hp else "original", "ratio": r, "size": res["size"],
                             "reframe": res["mode"], "duration_s": round(info["duration"], 2),
                             "placements": PLACEMENTS[r]})
                print(f"Wrote {out_dir / fname}", file=sys.stderr)
    with (out_dir / "manifest.csv").open("w", newline="", encoding="utf-8") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    (out_dir / "manifest.json").write_text(json.dumps({"body": str(body), "cut": a.cut, "variants": rows}, indent=2),
                                           encoding="utf-8")
    print(json.dumps({"variants": len(rows), "hooks": len(hooks), "ratios": ratios,
                      "manifest": str(out_dir / "manifest.csv")}, indent=2))


def main():
    ap = argparse.ArgumentParser(description="Ad variations: hook swaps + aspect ratios (local ffmpeg)")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("probe"); p.add_argument("videos", nargs="+"); p.set_defaults(fn=cmd_probe)

    p = sub.add_parser("suggest-cut", help="candidate end points of the original hook")
    p.add_argument("video"); p.add_argument("--max", type=float, default=8.0, help="search the first N seconds")
    p.add_argument("--threshold", type=float, default=0.3, help="scene-change sensitivity (lower = more)")
    p.set_defaults(fn=cmd_suggest_cut)

    p = sub.add_parser("frame", help="save one frame as JPG")
    p.add_argument("video"); p.add_argument("--at", type=float, default=0.0); p.add_argument("--out", required=True)
    p.set_defaults(fn=cmd_frame)

    p = sub.add_parser("trim", help="cut a clip to start..end seconds (e.g. a generated hook that runs long)")
    p.add_argument("video"); p.add_argument("--start", type=float, default=0.0)
    p.add_argument("--end", type=float, help="end time in seconds (default: clip end)")
    p.add_argument("--fade", type=float, default=0.08, help="audio fade-out seconds at the end (0 = none)")
    p.add_argument("--out", required=True); p.set_defaults(fn=cmd_trim)

    p = sub.add_parser("splice", help="replace the first --cut seconds of --body with --hook")
    p.add_argument("--hook", required=True); p.add_argument("--body", required=True)
    p.add_argument("--cut", type=float, required=True, help="seconds of the body's original hook to drop")
    p.add_argument("--out", required=True); p.set_defaults(fn=cmd_splice)

    for name, fn, hlp in (("reframe", cmd_reframe, "aspect-ratio versions of one video"),
                          ("matrix", cmd_matrix, "hooks x ratios + manifest")):
        p = sub.add_parser(name, help=hlp)
        if name == "reframe":
            p.add_argument("video")
        else:
            p.add_argument("--body", required=True, help="the approved ad")
            p.add_argument("--cut", type=float, default=0.0, help="end of the original hook in the body (seconds)")
            p.add_argument("--hooks", nargs="*", help="new hook clips")
            p.add_argument("--include-original", action="store_true", help="also output the untouched ad")
        p.add_argument("--ratios", default="9:16,1:1,4:5,16:9")
        p.add_argument("--mode", choices=["blur", "crop", "pad"], default="blur",
                       help="blur = blurred fill (default), crop = fill by cropping, pad = black bars")
        p.add_argument("--focus-x", type=float, default=0.5, help="crop mode: 0 = keep left, 1 = keep right")
        p.add_argument("--focus-y", type=float, default=0.5, help="crop mode: 0 = keep top, 1 = keep bottom")
        p.add_argument("--name", help="base name for output files")
        p.add_argument("--out", required=True)
        p.set_defaults(fn=fn)

    a = ap.parse_args()
    need_tools()
    a.fn(a)


if __name__ == "__main__":
    main()
