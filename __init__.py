import importlib
import inspect
import sys
from pathlib import Path
import bpy

# from .lib import logging_settings

# logger = logging_settings.get_logger(__name__)


# モジュール読み込み
module_names = [
    "util",
    "logging_settings",
    "subprocess",
    "prop_json",
    "result",
    "exclude",
    "unittest",
    "target",
    "pose_checker",
    "dialog",
    "panel",
    "prefs",
]
namespace = globals()
for name in module_names:
    fullname = '{}.{}.{}'.format(__package__, "lib", name)
    if fullname in sys.modules:
        namespace[name] = importlib.reload(sys.modules[fullname])
    else:
        namespace[name] = importlib.import_module(fullname)

# アドオン情報
bl_info = {
    'name': 'Taremin Pose Checker',
    'category': '3D View',
    'author': 'Taremin',
    'location': 'View 3D > Taremin',
    'description': "Check objects overlapping by pose library",
    'version': (0, 0, 1),
    'blender': (2, 80, 0),
    'wiki_url': '',
    'tracker_url': '',
    'warning': '',
}


# クラスの登録
classes = [
    # このファイル内のBlenderクラス
]
for module in module_names:
    for module_class in [obj for name, obj in inspect.getmembers(namespace[module], inspect.isclass) if hasattr(obj, "bl_rna")]:
        classes.append(module_class)


print(classes)


def register():
    for value in classes:
        retry = 0
        while True:
            try:
                bpy.utils.register_class(value)
                print("Register:", value)
                break
            except ValueError:
                bpy.utils.unregister_class(value)
                retry += 1
                if retry > 1:
                    break
    props = namespace["panel"]
    bpy.types.Scene.taremin_pc = bpy.props.PointerProperty(
        type=props.TareminPoseCheckerPanelProps)


def unregister():
    for value in classes:
        print("Unregister:", value)
        try:
            bpy.utils.unregister_class(value)
        except RuntimeError:
            pass

    del bpy.types.Scene.taremin_pc
    Path(__file__).touch()


if __name__ == '__main__':
    register()
