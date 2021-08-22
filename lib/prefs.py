import bpy
from . import util


class TareminPoseCheckerPreferences(bpy.types.AddonPreferences):
    bl_idname = util.get_addon_name()

    is_debug: bpy.props.BoolProperty(
        name="Debug mode",  # TODO
        default=False,
    )

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "is_debug")
