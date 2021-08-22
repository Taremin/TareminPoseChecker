import bpy
import sys
import argparse
import os


def main():
    sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
    import prop_json

    argv = sys.argv
    if "--" not in argv:
        argv = []
    else:
        argv = argv[argv.index("--") + 1:]

    parser = argparse.ArgumentParser()

    options = {
        "target_index": int
    }

    for i, v in options.items():
        parser.add_argument("--" + i, type=v)

    args = parser.parse_args(argv)

    if hasattr(args, "target_index"):
        bpy.ops.taremin.pose_checker_run_target_test_background(
            target_index=args.target_index)
    else:
        print("parameter not found:", "target_index")

    json_basename, json_extname = os.path.splitext(bpy.data.filepath)
    json_path = json_basename + ".json"
    print("JSON path(Background):", json_path)

    json_str = prop_json.property_to_json(bpy.context.scene.taremin_pc)
    with open(json_path, "w", encoding='UTF-8') as file:
        file.write(json_str)

    bpy.ops.wm.save_as_mainfile()

    exit()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Background Error:", e)
