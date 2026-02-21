import sys
import json
import tempfile
import zipfile
import subprocess
from pathlib import Path


def compile_to_stl(scad_path: str) -> str:
    """Compile an OpenSCAD file to STL using the OpenSCAD CLI."""
    scad = Path(scad_path)
    stl = scad.with_suffix(".stl")

    result = subprocess.run(
        ["openscad", "-o", str(stl), str(scad)],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"OpenSCAD compilation failed:\n{result.stderr or result.stdout}"
        )

    print(f"    Compiled STL to {stl}")
    return str(stl)


def slice_to_gcode(stl_path: str) -> str:
    """Slice an STL file to G-code using OrcaSlicer CLI."""
    stl = Path(stl_path)
    gcode = stl.with_suffix(".gcode")

    profiles_dir = Path("/Applications/OrcaSlicer.app/Contents/Resources/profiles/BBL")
    process = profiles_dir / "process" / "0.20mm Standard @BBL A1M.json"
    filament = profiles_dir / "filament" / "Bambu PLA Basic @BBL A1M.json"

    # Patch the machine profile to add G92 E0 before each layer change,
    # required when use_relative_e_distances is enabled (Bambu default).
    base_machine = profiles_dir / "machine" / "Bambu Lab A1 mini 0.4 nozzle.json"
    with open(base_machine) as f:
        machine_data = json.load(f)
    machine_data["before_layer_change_gcode"] = "G92 E0"

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False, dir=stl.parent
    ) as tmp:
        json.dump(machine_data, tmp)
        patched_machine = tmp.name

    # Also patch process profile for brim
    with open(process) as f:
        process_data = json.load(f)
    process_data["brim_type"] = "outer_only"
    process_data["brim_width"] = "5"  # 5mm brim

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, dir=stl.parent) as tmp2:
        json.dump(process_data, tmp2)
        patched_process = tmp2.name

    result = subprocess.run(
        [
            "orca-slicer",
            "--load-settings", f"{patched_machine};{patched_process}",
            "--load-filaments", str(filament),
            "--slice", "0",
            "--outputdir", str(stl.parent),
            str(stl),
        ],
        capture_output=True,
        text=True,
    )

    Path(patched_machine).unlink(missing_ok=True)
    Path(patched_process).unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(
            f"OrcaSlicer slicing failed:\n{result.stderr or result.stdout}"
        )

    # OrcaSlicer may place the output in the same dir as the input
    if not gcode.exists():
        # try to find any .gcode file produced in the same directory
        candidates = list(stl.parent.glob("*.gcode"))
        if not candidates:
            raise RuntimeError("OrcaSlicer ran but no .gcode output was found.")
        gcode = max(candidates, key=lambda p: p.stat().st_mtime)

    print(f"    Sliced G-code to {gcode}")

    # Wrap gcode in a minimal 3MF (ZIP) — the Bambu printer requires this format
    tmf_path = gcode.parent / f"{gcode.stem}.gcode.3mf"
    with zipfile.ZipFile(tmf_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(gcode, "Metadata/plate_1.gcode")
    print(f"    Wrapped as 3MF: {tmf_path}")

    return str(tmf_path)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python slicer.py <path/to/file.scad>")
        sys.exit(1)

    scad_path = sys.argv[1]
    print(f"Compiling {scad_path} to STL...")
    stl_path = compile_to_stl(scad_path)

    print(f"Slicing {stl_path} to G-code...")
    gcode_path = slice_to_gcode(stl_path)

    print(f"\nDone: {gcode_path}")
