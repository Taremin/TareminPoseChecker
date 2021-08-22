import bpy

from . import exclude, util, pose_checker, result


class TareminPoseChecker_OT_SelectPoseDialog(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_select_pose_dialog"
    bl_label = "TareminPoseChecker_OT_SelectPoseDialog"
    bl_description = util.read_resource("panel", "select_pose_dialog", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={"HIDDEN"})
    test_index: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        target = util.get_addon_props(context).targets[self.target_index]
        test = target.tests[self.test_index]
        layout = self.layout

        for i, r in enumerate(test.results):
            # skip ok
            if r.result:
                continue

            box = layout.box()

            row = box.row()

            col = row.column(align=True)
            col.label(text=r.pose_name, translate=False)

            col = row.column(align=True)
            col = col.row(align=True)

            op = col.operator(
                exclude.TareminPoseChecker_OT_ExcludeList_Add.bl_idname, text="", icon="X")
            op.target_index = self.target_index
            op.test_index = self.test_index
            op.result_index = i

            op = col.operator(
                pose_checker.TareminPoseChecker_OT_ViewTestResult.bl_idname, text="", icon="OUTLINER_OB_ARMATURE")
            op.target_index = self.target_index
            op.test_index = self.test_index
            op.result_index = i
            op.mesh_only = False
            op.edit_mode = False

            op = col.operator(
                pose_checker.TareminPoseChecker_OT_ViewTestResult.bl_idname, text="", icon="OUTLINER_OB_MESH")
            op.target_index = self.target_index
            op.test_index = self.test_index
            op.result_index = i
            op.mesh_only = True
            op.edit_mode = False

            op = col.operator(
                pose_checker.TareminPoseChecker_OT_ViewTestResult.bl_idname, text="", icon="SHADING_WIRE")
            op.target_index = self.target_index
            op.test_index = self.test_index
            op.result_index = i
            op.mesh_only = True
            op.edit_mode = True

            row = box.row()
            col = row.column(align=True)
            col.prop(r, "object1", icon_only=True)
            col.enabled = False

            col = row.column(align=True)
            col.prop(r, "object2", icon_only=True)
            col.enabled = False

        op = layout.operator(
            result.TareminPoseChecker_OT_Result_Clear.bl_idname,
            text="Clear Results",
        )
        op.target_index = self.target_index
        op.test_index = self.test_index
