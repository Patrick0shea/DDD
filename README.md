# Autonomous 3D Printing Pipeline

Give Claude a text prompt → get a physical print on your Bambu Lab A1 Mini.

**Pipeline:** Prompt → Claude generates OpenSCAD → compiled to STL → sliced to G-code → uploaded to printer → print starts.

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

## Usage

```bash
# Full pipeline
python main.py "a 30mm solid cylinder with a 5mm hole through the center"

# Or run interactively
python main.py
```

### Test individual stages

```bash
# Test AI generation only
python ai_generator.py "a 20mm calibration cube"

# Test slicing only (given a .scad file)
python slicer.py output/1234567890.scad

# Test printer upload only (given a .gcode.3mf file)
python printer.py output/1234567890.gcode.3mf
```

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

These skills are loaded automatically by Claude Code when the relevant prompt is used. The `skill/` directory follows the [Claude Code skills spec](https://docs.anthropic.com/en/docs/claude-code/skills).

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
