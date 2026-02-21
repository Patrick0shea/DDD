# Architecture

## Overview

Text prompt → G-code → physical print on a Bambu Lab A1 Mini.

```
User prompt
    │
    ▼
ai_generator.py   — calls Anthropic API (claude-sonnet-4-6), returns OpenSCAD source
    │
    ▼  .scad
slicer.py         — compiles .scad → .stl via OpenSCAD CLI
    │
    ▼  .stl
slicer.py         — slices .stl → .gcode via OrcaSlicer CLI
    │
    ▼  .gcode.3mf
printer.py        — uploads .gcode.3mf to printer over FTPS (port 990)
                  — sends print command over MQTT (port 8883, TLS)
                  — monitors print status via thread_monitor.py
```

Entry point: `main.py`

---

## Files

| File | Role |
|---|---|
| `main.py` | Orchestrates the four-stage pipeline |
| `ai_generator.py` | Anthropic API call → OpenSCAD source file |
| `slicer.py` | `openscad` CLI → STL, then `orca-slicer` CLI → G-code |
| `printer.py` | FTPS upload + MQTT print command to Bambu printer |
| `thread_monitor.py` | Polls printer status over MQTT until print completes |
| `config.py` | Loads env vars from `.env` |
| `output/` | All generated files (`.scad`, `.stl`, `.gcode`, `.gcode.3mf`), named by Unix timestamp |

---

## External dependencies

| Tool | Used for |
|---|---|
| `openscad` CLI | Compiles OpenSCAD source to STL mesh |
| `orca-slicer` CLI | Slices STL to printer G-code using Bambu A1 Mini profiles |
| Anthropic API | Generates OpenSCAD from natural language prompt |
| `pybambu` | Bambu printer communication (MQTT + FTPS) |
| `paho-mqtt` | MQTT client for printer status monitoring |
| `python-dotenv` | Loads `.env` credentials |

---

## OrcaSlicer profile stack

OrcaSlicer is called with patched versions of the bundled Bambu profiles:

1. **Machine profile** (`BBL/machine/Bambu Lab A1 mini 0.4 nozzle.json`) — patched at runtime to add `G92 E0` as `before_layer_change_gcode`, required when `use_relative_e_distances` is enabled (Bambu default).
2. **Process profile** (`BBL/process/0.20mm Standard @BBL A1M.json`) — patched at runtime to set `brim_type: outer_only` and `brim_width: 5` (5mm brim for first-layer adhesion).
3. **Filament profile** (`BBL/filament/Bambu PLA Basic @BBL A1M.json`) — used as-is.

Both patched profiles are written to temp files alongside the STL and deleted after slicing.

---

## Printer communication

The Bambu A1 Mini uses two protocols over the local network:

- **FTPS (port 990)** — file upload. The G-code (wrapped in a minimal 3MF ZIP) is transferred to the printer's internal storage before printing starts.
- **MQTT (port 8883, TLS)** — command and status. Print commands are sent as JSON messages; status (progress, errors, stage) is received as JSON. Bambu uses a self-signed certificate so TLS verification is disabled.

LAN Mode must be enabled on the printer (Settings → Network → LAN Mode).

---

## Credentials (`.env`)

```
ANTHROPIC_API_KEY   — Anthropic API key (sk-ant-...)
BAMBU_IP            — Printer local IP address
BAMBU_SERIAL        — Printer serial number (from printer touchscreen or label)
BAMBU_ACCESS_CODE   — 8-digit LAN access code (from printer touchscreen)
```
