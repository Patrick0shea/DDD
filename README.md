# DDD — Describe. Design. Deliver.

Give Claude a text prompt → get a physical print on your Bambu Lab A1 Mini.

**Pipeline:** Prompt → Claude generates OpenSCAD → compiled to STL → sliced to G-code → uploaded to printer → print starts.

## How it works

The backend (`server.py`) must run on a machine **on the same local network as your printer**. This is unavoidable — the printer only accepts connections over LAN.

```
Your browser
    │  HTTP
    ▼
server.py  (your machine, same network as printer)
    │  FTPS / MQTT
    ▼
Bambu Lab A1 Mini
```

Opening `index.html` directly in a browser shows a **demo mode** with a simulated pipeline — no backend or printer needed. To run real prints, start `server.py` first.

## Prerequisites

- Python 3.10+
- [OpenSCAD](https://openscad.org/downloads.html) — install and ensure `openscad` is on your PATH
- [OrcaSlicer](https://github.com/SoftFever/OrcaSlicer/releases) — install and ensure `orca-slicer` is on your PATH
- Bambu Lab A1 Mini on the same local network
- An Anthropic API key

### Verify CLI tools are available

```bash
openscad --version
orca-slicer --version
```

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your values:

```
ANTHROPIC_API_KEY=sk-ant-...
BAMBU_IP=192.168.x.x
BAMBU_SERIAL=01P00A...
BAMBU_ACCESS_CODE=12345678
```

### Finding your printer credentials

| Value | Where to find it |
|---|---|
| `BAMBU_IP` | Your router's DHCP table, or Bambu Handy app → Device → LAN info |
| `BAMBU_SERIAL` | Printer touchscreen → Settings → Device, or the label on the printer |
| `BAMBU_ACCESS_CODE` | Printer touchscreen → Settings → Device → Access Code |

> **LAN Mode**: The printer must have LAN Mode enabled. On the touchscreen go to Settings → Network → LAN Mode and toggle it on.

## Running locally

```bash
python server.py
# open http://localhost:5000
```

The frontend auto-detects the backend. Status dot turns green when connected.

### CLI usage (no web UI)

```bash
# Full pipeline
python main.py "a 30mm solid cylinder with a 5mm hole through the center"

# Test individual stages
python ai_generator.py "a 20mm calibration cube"
python slicer.py output/1234567890.scad
python printer.py output/1234567890.gcode.3mf
```

## Using from anywhere (remote access)

Since the backend must stay on your local network, the way to use it remotely is to expose your local server to the internet with a tunnel.

**Cloudflare Tunnel** (recommended — free, no account, no port forwarding, URL is stable per session):

1. Install `cloudflared`:
   ```bash
   # macOS
   brew install cloudflare/cloudflare/cloudflared

   # Linux
   wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
   sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared
   sudo chmod +x /usr/local/bin/cloudflared

   # Windows — download the installer:
   # https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/
   ```

2. Start your server and the tunnel in two terminals:
   ```bash
   # terminal 1
   python server.py

   # terminal 2
   cloudflared tunnel --url http://localhost:5000
   ```

3. Cloudflare prints a URL like `https://abc-def-123.trycloudflare.com` — open that on any device, anywhere.

> The URL changes each time you restart the tunnel. If you want a permanent custom domain (e.g. `print.yourdomain.com`), create a free Cloudflare account and set up a named tunnel — [see the docs](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/get-started/).

**ngrok** (alternative — simpler setup, URL changes on every restart on the free tier):
```bash
ngrok http 5000
```

Either way: `server.py` keeps running on your home machine next to the printer. The tunnel just gives you a public HTTPS URL to reach it from your phone, laptop, wherever.

## Output files

All generated files are saved to `./output/`:
- `{timestamp}.scad` — OpenSCAD source
- `{timestamp}.stl` — compiled mesh
- `{timestamp}.gcode` — sliced G-code
- `{timestamp}.gcode.3mf` — G-code wrapped in 3MF format (required by Bambu printers)

## Let Claude decide what to print

The pipeline includes a set of Claude Code skills that give your agent creative autonomy — the same idea as [Claude making its own drawings](https://www.anthropic.com/news/claude-draws), but in physical plastic.

Give Claude access to a printer and step back:

```
"You have access to a 3D printer. Make something that represents you."
```

Three modes are defined in `skill/`:

| Skill | What it does |
|---|---|
| `SKILL.md` | **Self-portrait** — Claude reflects on its own nature and externalises it as an object. It thinks before coding, signs the work, and iterates from your photos of the print. |
| `RESPOND.md` | **Response** — Claude makes something *about* an idea, a conversation, or something in the world. Not a self-portrait but a physical argument. |
| `SERIES.md` | **Series** — Claude builds a body of work across multiple prints, holding a shared constraint and learning from each iteration. |

These skills are loaded automatically by Claude Code when the relevant prompt is used.

## Print quality

The AI is prompted to generate FDM-friendly geometry:
- Walls ≥ 1.6mm thick (4 perimeters at 0.4mm nozzle)
- CSG primitives only — no complex polyhedra
- No overhangs > 45° (no supports needed)
- Flat base flush on the bed

The slicer adds a 5mm brim automatically to anchor the first layer.

## Platform notes

The OrcaSlicer profiles directory is detected automatically per platform:

| OS | Default path |
|---|---|
| macOS | `/Applications/OrcaSlicer.app/Contents/Resources/profiles/BBL` |
| Linux | `~/.local/share/OrcaSlicer/system/BBL` |
| Windows | `C:\Program Files\OrcaSlicer\resources\profiles\BBL` |

If your install is in a non-standard location, set `ORCASLICER_PROFILES` in your `.env`:
```
ORCASLICER_PROFILES=/path/to/your/OrcaSlicer/profiles/BBL
```

## Notes

- The printer communicates over MQTT (port 8883, TLS) and FTPS (port 990). Both use Bambu's self-signed certificate, so TLS verification is disabled.
- If the print is already running when you Ctrl+C out of the status monitor, the print continues on the printer.
