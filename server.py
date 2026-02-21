"""
print-agent web server
----------------------
Serves the frontend and runs the print pipeline via SSE.

Usage:
    python server.py

Then open http://localhost:5000 in your browser.

To expose publicly (e.g. for a Vercel-hosted frontend):
    ngrok http 5000
"""
import json
import sys
import os
from pathlib import Path
from flask import Flask, request, Response, stream_with_context, send_from_directory

app = Flask(__name__, static_folder=".")


def _cors(resp: Response) -> Response:
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
    resp.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    return resp


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


# ── Static frontend ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


# ── Health check ──────────────────────────────────────────────────────────────

@app.route("/api/health")
def health():
    return _cors(Response(json.dumps({"ok": True}), mimetype="application/json"))


# ── Abort ─────────────────────────────────────────────────────────────────────

@app.route("/api/abort", methods=["POST", "OPTIONS"])
def abort_endpoint():
    if request.method == "OPTIONS":
        return _cors(Response())
    try:
        from printer import cancel_print
        cancel_print()
        return _cors(Response(json.dumps({"ok": True}), mimetype="application/json"))
    except Exception as e:
        return _cors(Response(json.dumps({"error": str(e)}), status=500, mimetype="application/json"))


# ── Print pipeline ────────────────────────────────────────────────────────────

@app.route("/api/print", methods=["POST", "OPTIONS"])
def print_endpoint():
    if request.method == "OPTIONS":
        return _cors(Response())

    body = request.get_json(silent=True) or {}
    prompt = (body.get("prompt") or "").strip()
    if not prompt:
        return _cors(
            Response(
                json.dumps({"error": "prompt is required"}),
                status=400,
                mimetype="application/json",
            )
        )

    def generate():
        try:
            # ── Stage 1: Generate OpenSCAD ────────────────
            yield _sse({"stage": 0, "status": "active", "detail": "calling claude api..."})
            from ai_generator import generate_openscad
            scad_path = generate_openscad(prompt)
            yield _sse({
                "stage": 0, "status": "done",
                "message": f"saved {Path(scad_path).name}",
                "detail": scad_path,
            })

            # ── Stage 2: Compile STL ──────────────────────
            yield _sse({"stage": 1, "status": "active", "detail": "running openscad cli..."})
            from slicer import compile_to_stl
            stl_path = compile_to_stl(scad_path)
            yield _sse({
                "stage": 1, "status": "done",
                "message": f"saved {Path(stl_path).name}",
                "detail": stl_path,
            })

            # ── Stage 3: Slice to G-code ──────────────────
            yield _sse({"stage": 2, "status": "active", "detail": "orca-slicer slicing..."})
            from slicer import slice_to_gcode
            gcode_path = slice_to_gcode(stl_path)
            yield _sse({
                "stage": 2, "status": "done",
                "message": f"saved {Path(gcode_path).name}",
                "detail": gcode_path,
            })

            # ── Stage 4: Upload + Print ───────────────────
            yield _sse({"stage": 3, "status": "active", "detail": "uploading over ftps..."})
            from printer import upload_and_print
            upload_and_print(gcode_path)
            yield _sse({
                "stage": 3, "status": "done",
                "message": "print started",
                "detail": "printing in progress",
            })

            yield _sse({"done": True})

        except Exception as e:
            yield _sse({"error": str(e)})

    resp = Response(stream_with_context(generate()), mimetype="text/event-stream")
    resp.headers["Cache-Control"] = "no-cache"
    resp.headers["X-Accel-Buffering"] = "no"
    return _cors(resp)


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n  print-agent running → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
