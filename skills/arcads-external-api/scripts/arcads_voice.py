#!/usr/bin/env python3
"""Arcads voice + lip-sync helper (standard library only; Python 3.9+).

Wraps the talking-actor endpoints of the Arcads external API so the agent does not hand-write
curl calls. Credentials come from .env at the repo root (ARCADS_BASIC_AUTH or ARCADS_API_KEY),
exactly like scripts/check-arcads-env.sh. Nothing secret is printed.

Commands (run from the repo root):

  # Browse lip-sync-ready actors (stock) or your workspace's own actors
  python3 skills/arcads-external-api/scripts/arcads_voice.py actors --gender Female --age "Young Adult"
  python3 skills/arcads-external-api/scripts/arcads_voice.py actors --mine

  # Browse voices
  python3 skills/arcads-external-api/scripts/arcads_voice.py voices --language English --gender Female

  # Clone a voice from your own samples (you must own or have rights to the voice)
  python3 skills/arcads-external-api/scripts/arcads_voice.py clone-voice --name "Brand narrator" \
      --language English --gender Female references/voices/narrator-1.mp3 references/voices/narrator-2.mp3

  # Generate talking-actor videos (one per --actor). Use --script for text, or --audio for a
  # voiceover file (e.g. made with the chatterbox-voiceover skill). --dry-run prints the request only.
  python3 skills/arcads-external-api/scripts/arcads_voice.py talk --product <productId> \
      --actor <situationId>[:<voiceId>] --script "..." --model arcads_1.0 --wait --out output/talking

  # Check / fetch an existing generation
  python3 skills/arcads-external-api/scripts/arcads_voice.py status <id>
  python3 skills/arcads-external-api/scripts/arcads_voice.py fetch <id> --out output/talking
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MODELS = ("arcads_1.0", "audio_driven", "omnihuman")
AUDIO_TYPES = {
    ".mp3": "audio/mpeg", ".wav": "audio/wav", ".m4a": "audio/m4a", ".aac": "audio/aac",
    ".ogg": "audio/ogg", ".flac": "audio/flac", ".webm": "audio/webm", ".opus": "audio/opus",
    ".mp4": "video/mp4", ".mov": "video/quicktime",
}


# ── config ──────────────────────────────────────────────────────────────────
def load_env() -> None:
    env = ROOT / ".env"
    if not env.is_file():
        return
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, val = line.split("=", 1)
        key, val = key.strip().removeprefix("export ").strip(), val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "'\"":
            val = val[1:-1]
        os.environ.setdefault(key, val)


def auth_header() -> str:
    basic = os.environ.get("ARCADS_BASIC_AUTH", "")
    if basic and "your_base64_encoded_credentials_here" not in basic:
        return basic if basic.lower().startswith("basic ") else f"Basic {basic}"
    key = os.environ.get("ARCADS_API_KEY", "")
    if key and key != "your_key_here":
        return "Basic " + base64.b64encode(f"{key}:".encode()).decode()
    sys.exit("No Arcads credentials found. Run ./scripts/setup.sh (or fill in .env), then retry.")


def base_url() -> str:
    return os.environ.get("ARCADS_BASE_URL", "https://external-api.arcads.ai").rstrip("/")


# ── http ────────────────────────────────────────────────────────────────────
class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):  # surface 302s so we can read Location
        return None


def api(method: str, path: str, body=None, query=None, follow=True, soft=False):
    url = base_url() + path
    if query:
        url += "?" + urllib.parse.urlencode([(k, v) for k, vs in query.items() for v in (vs if isinstance(vs, list) else [vs]) if v is not None])
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", auth_header())
    req.add_header("Accept", "application/json")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    opener = urllib.request.build_opener() if follow else urllib.request.build_opener(NoRedirect)
    try:
        with opener.open(req, timeout=120) as r:
            raw = r.read()
            return r.status, (json.loads(raw) if raw and raw[:1] in b"[{" else raw.decode(errors="replace")), r.headers
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308):
            return e.code, "", e.headers
        detail = e.read().decode(errors="replace")[:600]
        if soft:
            return e.code, None, e.headers
        sys.exit(f"{method} {path} -> HTTP {e.code}: {detail}")


def upload(path: Path) -> str:
    """Presigned upload; returns the filePath to pass to Arcads."""
    ftype = AUDIO_TYPES.get(path.suffix.lower()) or mimetypes.guess_type(path.name)[0]
    if not ftype:
        sys.exit(f"Unsupported file type: {path.name}")
    _, res, _ = api("POST", "/v1/file-upload/get-presigned-url", {"fileType": ftype})
    put = urllib.request.Request(res["presignedUrl"], data=path.read_bytes(), method="PUT")
    put.add_header("Content-Type", ftype)
    with urllib.request.urlopen(put, timeout=300) as r:
        if r.status >= 300:
            sys.exit(f"Upload of {path.name} failed: HTTP {r.status}")
    print(f"Uploaded {path.name} -> {res['filePath']}", file=sys.stderr)
    return res["filePath"]


# ── cost log (logs/arcads-api.jsonl; see logs/README.md) ────────────────────
LOG = ROOT / "logs" / "arcads-api.jsonl"


def log_start(item: dict, body: dict, script: str | None):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "endpoint": "POST /v2/talking-actors/generate",
        "model": item.get("model") or body["model"],
        "assetId": item.get("id"),
        "productId": body["productId"],
        "projectId": body.get("projectId"),
        "request": {
            "actorsInRequest": len(body["actors"]),
            "customVoice": any("voiceId" in x for x in body["actors"]),
            "referenceAudiosCount": len(body.get("referenceAudios", [])),
            "scriptWordCount": len(script.split()) if script else 0,
            "autoAddScriptEmotion": bool(body.get("autoAddScriptEmotion")),
        },
        "response": {"status": item.get("status"), "creditsCharged": None, "generationTimeSec": None, "error": None},
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def log_finish(gid: str, status: str, seconds: int, error: str | None = None):
    """Update the entry for gid in place with the final status (and credits, if the asset reports them)."""
    if not LOG.is_file():
        return
    credits = None
    try:
        _, asset, _ = api("GET", f"/v1/assets/{gid}", soft=True)
        if isinstance(asset, dict):
            credits = asset.get("creditsCharged")
    except Exception:  # best effort: talking-actor ids may not be readable as assets
        pass
    lines = LOG.read_text(encoding="utf-8").splitlines()
    for i in range(len(lines) - 1, -1, -1):
        try:
            e = json.loads(lines[i])
        except ValueError:
            continue
        if e.get("assetId") == gid:
            e["response"].update(status=status, generationTimeSec=seconds, error=error)
            if credits is not None:
                e["response"]["creditsCharged"] = credits
            lines[i] = json.dumps(e)
            LOG.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return


# ── commands ────────────────────────────────────────────────────────────────
def cmd_actors(a):
    if a.mine:
        _, res, _ = api("GET", "/v1/situations/mine", query={"page": a.page, "pageSize": a.page_size})
    else:
        _, res, _ = api("GET", "/v1/situations", query={
            "page": a.page, "pageSize": a.page_size, "talkingActorEnabled": "true",
            "actorGender": a.gender, "actorAge": a.age, "actorName": a.name,
        })
    items = res.get("items", [])
    if a.json:
        print(json.dumps(res, indent=2)); return
    print(f"{res.get('count', len(items))} situations (showing {len(items)})")
    for s in items:
        act = s.get("actor") or {}
        tags = ", ".join((s.get("tags") or [])[:4])
        emo = ", ".join((s.get("emotions") or [])[:2])
        print(f"- {s['id']}  {act.get('name', '?')} | {act.get('gender', '')} {act.get('age', '')} | "
              f"{s.get('cameraAngle') or ''} | {tags} | {emo} | preview: {s.get('previewUrl', '')}")


def cmd_voices(a):
    _, res, _ = api("GET", "/v1/voices", query={"page": a.page, "pageSize": a.page_size,
                                                "language": a.language, "gender": a.gender, "age": a.age})
    if a.json:
        print(json.dumps(res, indent=2)); return
    items = res.get("items", [])
    print(f"{res.get('count', len(items))} voices (showing {len(items)})")
    for v in items:
        exp = f" | expires {v['expiresAt']}" if v.get("expiresAt") else ""
        print(f"- {v['id']}  {v.get('name')} | {v.get('gender') or ''} {v.get('age') or ''} {v.get('accent') or ''} "
              f"| {v.get('language') or ''} | {(v.get('descriptive') or '')[:60]} | sample: {v.get('audioUrl', '')}{exp}")


def cmd_clone(a):
    paths = [upload(Path(p)) for p in a.samples]
    body = {"name": a.name, "language": a.language, "audioS3FilePaths": paths}
    if a.gender:
        body["gender"] = a.gender
    _, res, _ = api("POST", "/v1/voices/clone", body)
    print(json.dumps(res, indent=2))
    if res.get("expiresAt"):
        print(f"Note: API-cloned voices are temporary (expires {res['expiresAt']}).", file=sys.stderr)


def parse_actor(spec: str) -> dict:
    situation, _, voice = spec.partition(":")
    d = {"situationId": situation.strip()}
    if voice.strip():
        d["voiceId"] = voice.strip()
    return d


def cmd_talk(a):
    if bool(a.script) == bool(a.audio):
        sys.exit("Pass exactly one of --script or --audio.")
    body = {"model": a.model, "productId": a.product, "actors": [parse_actor(x) for x in a.actor]}
    if a.project:
        body["projectId"] = a.project
    if a.script:
        body["script"] = a.script
    if a.emotion:
        body["autoAddScriptEmotion"] = True
    if a.dry_run:
        if a.audio:
            body["referenceAudios"] = [f"<upload of {a.audio}>"]
        print(json.dumps(body, indent=2)); return
    if a.audio:
        body["referenceAudios"] = [upload(Path(a.audio))]
    _, res, _ = api("POST", "/v2/talking-actors/generate", body)
    items = res if isinstance(res, list) else [res]
    for it in items:
        print(f"Started {it.get('id')} ({it.get('model')}): {it.get('status')}")
        log_start(it, body, a.script)
    if a.wait:
        for it in items:
            wait_and_fetch(it["id"], a.out, a.timeout)


def wait_and_fetch(gid: str, out: str | None, timeout: int):
    start, delay = time.time(), 10
    while True:
        _, st, _ = api("GET", f"/v2/talking-actors/{gid}")
        status = st.get("status")
        print(f"{gid}: {status} ({int(time.time() - start)}s)", file=sys.stderr)
        if status == "completed":
            log_finish(gid, "completed", int(time.time() - start))
            break
        if status == "failed":
            log_finish(gid, "failed", int(time.time() - start), st.get("error"))
            sys.exit(f"{gid} failed: {st.get('error') or 'no error message'}")
        if time.time() - start > timeout:
            sys.exit(f"Timed out after {timeout}s; check later with: status {gid}")
        time.sleep(delay)
        delay = min(delay + 5, 30)
    fetch(gid, out)


def watch_url(gid: str) -> str:
    code, _, headers = api("GET", f"/v2/talking-actors/{gid}/watch", follow=False)
    loc = headers.get("Location") if headers else None
    if not loc:
        sys.exit(f"No watch URL returned for {gid} (HTTP {code}).")
    return loc


def fetch(gid: str, out: str | None):
    url = watch_url(gid)
    print(f"Watch: {url}")
    if not out:
        return
    dest = Path(out)
    dest.mkdir(parents=True, exist_ok=True)
    target = dest / f"talking-actor-{gid}.mp4"
    try:
        with urllib.request.urlopen(url, timeout=300) as r:
            ctype = r.headers.get("Content-Type", "")
            data = r.read()
        if not ctype.startswith("video/"):
            print(f"Watch URL is a web page ({ctype}); open it in a browser to download.", file=sys.stderr)
            return
        target.write_bytes(data)
        print(f"Saved {target}")
    except urllib.error.URLError as e:
        print(f"Could not download ({e}); open the watch URL instead.", file=sys.stderr)


def cmd_status(a):
    _, st, _ = api("GET", f"/v2/talking-actors/{a.id}")
    print(json.dumps(st, indent=2))


def cmd_fetch(a):
    fetch(a.id, a.out)


def main():
    load_env()
    ap = argparse.ArgumentParser(description="Arcads voice + lip-sync helper")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("actors", help="list lip-sync-ready situations (actors)")
    p.add_argument("--mine", action="store_true", help="your workspace's own situations")
    p.add_argument("--gender", action="append", choices=["Female", "Male"])
    p.add_argument("--age", action="append", choices=["Young Adult", "Adult", "Senior"])
    p.add_argument("--name")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_actors)

    p = sub.add_parser("voices", help="list voices")
    p.add_argument("--language", action="append")
    p.add_argument("--gender", action="append")
    p.add_argument("--age", action="append")
    p.add_argument("--page", type=int, default=1)
    p.add_argument("--page-size", type=int, default=20)
    p.add_argument("--json", action="store_true")
    p.set_defaults(fn=cmd_voices)

    p = sub.add_parser("clone-voice", help="clone a voice from audio/video samples you have rights to")
    p.add_argument("--name", required=True)
    p.add_argument("--language", required=True, help="e.g. English, Spanish, French")
    p.add_argument("--gender", choices=["Female", "Male", "Neutral"])
    p.add_argument("samples", nargs="+")
    p.set_defaults(fn=cmd_clone)

    p = sub.add_parser("talk", help="generate talking-actor (lip-synced) videos")
    p.add_argument("--product", required=True, help="Arcads productId (see MASTER_CONTEXT.md)")
    p.add_argument("--project", help="projectId to file the videos under")
    p.add_argument("--actor", action="append", required=True, help="situationId or situationId:voiceId (repeat for several)")
    p.add_argument("--script", help="text the actor says")
    p.add_argument("--audio", help="voiceover file to lip-sync instead of --script (max 1)")
    p.add_argument("--model", choices=MODELS, default="arcads_1.0")
    p.add_argument("--emotion", action="store_true", help="autoAddScriptEmotion")
    p.add_argument("--wait", action="store_true", help="poll until done, then fetch")
    p.add_argument("--out", help="folder to save finished videos")
    p.add_argument("--timeout", type=int, default=1200)
    p.add_argument("--dry-run", action="store_true", help="print the request body without calling the API")
    p.set_defaults(fn=cmd_talk)

    p = sub.add_parser("status", help="status of a talking-actor generation")
    p.add_argument("id")
    p.set_defaults(fn=cmd_status)

    p = sub.add_parser("fetch", help="get the watch URL (and save the video if --out)")
    p.add_argument("id")
    p.add_argument("--out")
    p.set_defaults(fn=cmd_fetch)

    a = ap.parse_args()
    if a.cmd == "talk" and a.dry_run:
        return a.fn(a)  # no credentials needed for a dry run
    a.fn(a)


if __name__ == "__main__":
    main()
