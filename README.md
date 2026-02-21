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

## Print quality

The AI is prompted to generate FDM-friendly geometry:
- Walls ≥ 1.6mm thick (4 perimeters at 0.4mm nozzle)
- CSG primitives only — no complex polyhedra
- No overhangs > 45° (no supports needed)
- Flat base flush on the bed

The slicer adds a 5mm brim automatically to anchor the first layer.

## Notes

- The printer communicates over MQTT (port 8883, TLS) and FTPS (port 990). Both use Bambu's self-signed certificate, so TLS verification is disabled.
- If the print is already running when you Ctrl+C out of the status monitor, the print continues on the printer.
