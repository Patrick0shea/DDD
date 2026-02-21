import sys
import time
from pathlib import Path
import anthropic
import config

SYSTEM_PROMPT = (
    "You are an expert OpenSCAD programmer generating models for FDM 3D printing on a Bambu Lab A1 Mini "
    "(0.4mm nozzle, 0.2mm layer height). Respond with ONLY valid OpenSCAD code, no explanation, no markdown. "
    "Rules: "
    "(1) All walls must be at least 1.6mm thick (4 perimeters). "
    "(2) Use CSG primitives (cube, sphere, cylinder, union, difference, intersection, rotate_extrude, linear_extrude) — avoid polyhedron unless absolutely necessary. "
    "(3) No overhangs greater than 45 degrees — the object must be printable without supports. "
    "(4) The object must have a flat base that sits flush on the print bed. "
    "(5) All dimensions in millimeters, keep the object within 150x150x150mm. "
    "(6) Define all key dimensions as variables at the top. "
    "(7) Include $fn = 64 for smooth curves."
)

OUTPUT_DIR = Path("output")


def generate_openscad(prompt: str) -> str:
    """Call Claude API with the given prompt and return raw OpenSCAD code."""
    client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    code = message.content[0].text.strip()
    # Strip markdown code fences if the model wrapped the output
    if code.startswith("```"):
        code = code.split("\n", 1)[1] if "\n" in code else code
        if code.endswith("```"):
            code = code[: code.rfind("```")]
        code = code.strip()

    OUTPUT_DIR.mkdir(exist_ok=True)
    timestamp = int(time.time())
    scad_path = OUTPUT_DIR / f"{timestamp}.scad"
    scad_path.write_text(code)
    print(f"    Saved OpenSCAD to {scad_path}")

    return str(scad_path)


if __name__ == "__main__":
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("Describe the part: ")
    path = generate_openscad(prompt)
    print(f"\nGenerated: {path}")
    print("\n--- OpenSCAD code ---")
    print(Path(path).read_text())
