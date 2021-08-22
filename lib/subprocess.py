import bpy
import os
import subprocess


def create_temp_name(dir, prefix, suffix):
    filenum = 0

    while True:
        filename = prefix + ("_%03i" % filenum) + suffix
        path = os.path.join(dir, filename)
        if not os.path.exists(path):
            break
        filenum = filenum + 1

    return path


def exec_subprocess(script, tempfile_prefix, tempfile_suffix, options={}):
    execfile = bpy.path.abspath(bpy.app.binary_path)
    tmpfile = create_temp_name(
        bpy.path.abspath(bpy.app.tempdir),
        tempfile_prefix,
        tempfile_suffix
    )

    print("Temporary file path:", tmpfile)
    bpy.ops.wm.save_as_mainfile(filepath=tmpfile, copy=True)

    exec = [
        execfile,
        tmpfile,
        "--background",
        "--python", script,
        "--",
    ]

    for key, value in options.items():
        exec.append("--" + key)
        exec.append(str(value))

    sub = subprocess.Popen(
        exec,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    out, err = sub.communicate()

    retcode = sub.wait(60)
    if err:
        print("Background Error:")
        print(err)
    if out:
        print("BackGroundOutput:")
        print(out)

    return tmpfile
