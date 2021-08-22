import bpy

from . import util


class TareminPoseCheckerUnitTestResultFaceIndexPair(bpy.types.PropertyGroup):
    index1: bpy.props.IntProperty()
    index2: bpy.props.IntProperty()


class TareminPoseCheckerUnitTestResultProps(bpy.types.PropertyGroup):
    object1: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=lambda self, obj: obj.type == 'MESH')
    object2: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=lambda self, obj: obj.type == 'MESH')
    pose_name: bpy.props.StringProperty(default="")
    result: bpy.props.BoolProperty(default=True)
    faces: bpy.props.CollectionProperty(
        type=TareminPoseCheckerUnitTestResultFaceIndexPair
    )


class TareminPoseChecker_OT_Result_Remove(bpy.types.Operator):
    bl_idname = 'taremin.pose_checker_result_remove'
    bl_label = "Remove Entry"
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={"HIDDEN"})
    test_index: bpy.props.IntProperty(options={"HIDDEN"})
    result_index: bpy.props.IntProperty(default=0, options={'HIDDEN'})

    def execute(self, context):
        settings = util.get_addon_props(context)
        target = settings.targets[self.target_index]
        test = target.tests[self.test_index]
        test.results.remove(self.result_index)

        return {'FINISHED'}


class TareminPoseChecker_OT_Result_Clear(bpy.types.Operator):
    bl_idname = 'taremin.pose_checker_result_clear'
    bl_label = "Clear Entry"
    bl_description = util.read_resource("panel", "result_clear", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={"HIDDEN"})
    test_index: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        settings = util.get_addon_props(context)
        target = settings.targets[self.target_index]
        test = target.tests[self.test_index]

        test.results.clear()
        context.area.tag_redraw()

        return {'FINISHED'}
