import bpy
from . import util


class TareminPoseCheckerExcludeSettingProps(bpy.types.PropertyGroup):
    object1: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=lambda self, obj: obj.type == 'MESH')
    object2: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=lambda self, obj: obj.type == 'MESH')
    pose_name: bpy.props.StringProperty()


class TareminPoseChecker_UL_ExcludeList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)
        col = row.column(align=True)
        col.prop(item, "object1", text="")

        col = row.column(align=True)
        col.prop(item, "object2", text="")

        col = row.column(align=True)
        col.prop(item, "pose_name", text="")

        col = row.column(align=False)
        op = col.operator(
            TareminPoseChecker_OT_ExcludeList_Remove.bl_idname,
            text="",
            icon="X",
        )
        settings = util.get_addon_props(context)
        op.target_index = list(settings.targets).index(data)
        op.excludes_index = index


class TareminPoseChecker_OT_ExcludeList_Add(bpy.types.Operator):
    bl_idname = 'taremin.pose_checker_exclude_list_add'
    bl_label = 'TareminPoseChecker_OT_ExcludeList_Add'
    bl_description = util.read_resource("panel", "result_exclude", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={"HIDDEN"})
    test_index: bpy.props.IntProperty(options={"HIDDEN"})
    result_index: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        settings = util.get_addon_props(context)
        target = settings.targets[self.target_index]
        test = target.tests[self.test_index]
        result = test.results[self.result_index]

        dict = util.create_exclude_dict(target)
        if not util.is_excluded(dict, result.object1, result.object2, result.pose_name):
            exclude = target.excludes.add()
            exclude.object1 = result.object1
            exclude.object2 = result.object2
            exclude.pose_name = result.pose_name

        test.results.remove(self.result_index)
        context.area.tag_redraw()

        return {'FINISHED'}


class TareminPoseChecker_OT_ExcludeList_Remove(bpy.types.Operator):
    bl_idname = 'taremin.pose_checker_exclude_list_remove'
    bl_label = "Remove Entry"
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={"HIDDEN"})
    excludes_index: bpy.props.IntProperty(default=0, options={'HIDDEN'})

    def execute(self, context):
        settings = util.get_addon_props(context)
        target = settings.targets[self.target_index]
        target.excludes.remove(self.excludes_index)

        return {'FINISHED'}
