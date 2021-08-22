import bpy
from . import exclude, unittest, util


class TareminPoseCheckerUnitTestTargetProps(bpy.types.PropertyGroup):
    armature: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=lambda self, obj: obj.type == 'ARMATURE')
    pose_library: bpy.props.PointerProperty(type=bpy.types.Action)
    folding: bpy.props.BoolProperty(default=False)

    tests: bpy.props.CollectionProperty(
        type=unittest.TareminPoseCheckerUnitTestProps)
    test_index: bpy.props.IntProperty()

    excludes: bpy.props.CollectionProperty(
        type=exclude.TareminPoseCheckerExcludeSettingProps
    )
    excludes_index: bpy.props.IntProperty()
    excludes_folding: bpy.props.BoolProperty(default=True)

    ignore_already_overlap: bpy.props.BoolProperty()


class TareminPoseChecker_OT_UnitTestTargetProps_Add(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_target_add"
    bl_label = "Add Entry"
    bl_description = util.read_resource("panel", "target_add", "label")
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return util.get_addon_props(context).index >= 0

    def execute(self, context):
        settings = util.get_addon_props(context)

        settings.targets.add()
        settings.index = len(settings.targets) - 1

        return {'FINISHED'}


class TareminPoseChecker_OT_UnitTestTargetProps_Remove(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_target_remove"
    bl_label = "Remove Entry"
    bl_description = util.read_resource("panel", "target_remove", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(default=0, options={'HIDDEN'})

    def execute(self, context):
        settings = util.get_addon_props(context)

        settings.targets.remove(self.target_index)
        max_index = len(settings.targets) - 1

        if settings.index > max_index:
            settings.index = max_index

        return {'FINISHED'}


class TareminPoseChecker_OT_UnitTestTargetProps_Clear_Results(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_target_clear_results"
    bl_label = "TareminPoseChecker_OT_UnitTestTargetProps_Clear_Results"
    bl_description = util.read_resource(
        "panel", "target_clear_result", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(default=0, options={'HIDDEN'})

    def execute(self, context):
        settings = util.get_addon_props(context)

        for test in settings.targets[self.target_index].tests:
            test.results.clear()

        return {'FINISHED'}


class TareminPoseChecker_OT_UnitTestTargetProps_Clear_All_Results(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_target_clear_all_results"
    bl_label = "TareminPoseChecker_OT_UnitTestTargetProps_Clear_All_Results"
    bl_description = util.read_resource("panel", "clear_all_results", "label")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        settings = util.get_addon_props(context)

        for target in settings.targets:
            for test in target.tests:
                test.results.clear()

        return {'FINISHED'}
