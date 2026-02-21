import sys
from pathlib import Path


def main():
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = input("Describe the part to print: ").strip()
        if not prompt:
            print("No prompt provided. Exiting.")
            sys.exit(1)

    Path("output").mkdir(exist_ok=True)

    try:
        print("\n[1/4] Generating OpenSCAD...")
        from ai_generator import generate_openscad
        scad_path = generate_openscad(prompt)

        print("\n[2/4] Compiling to STL...")
        from slicer import compile_to_stl
        stl_path = compile_to_stl(scad_path)

        print("\n[3/4] Slicing to G-code...")
        from slicer import slice_to_gcode
        gcode_path = slice_to_gcode(stl_path)

        print("\n[4/4] Uploading and starting print...")
        from printer import upload_and_print, poll_until_complete
        upload_and_print(gcode_path)

        print("\nWatching print progress...")
        poll_until_complete()

    except RuntimeError as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nAborted.")
        sys.exit(0)


if __name__ == "__main__":
    main()
