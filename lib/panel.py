import bpy
from . import pose_checker, target as target_props, unittest, util, dialog


class TareminPoseCheckerPanelProps(bpy.types.PropertyGroup):
    targets: bpy.props.CollectionProperty(
        type=target_props.TareminPoseCheckerUnitTestTargetProps)
    index: bpy.props.IntProperty(default=0)


class TareminPoseChecker_UL_UnitTestList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        row = layout.row(align=True)

        col = row.column()
        col.label(text="", icon="DOT")

        col = row.column(align=True)
        if item.is_collection1:
            col.prop(item, "collection1", text="")
        else:
            col.prop(item, "object1", text="")
        col = row.column(align=True)
        col.prop(item, "is_collection1",
                 icon="OUTLINER_COLLECTION", icon_only=True)

        col = row.column(align=True)
        if item.is_collection2:
            col.prop(item, "collection2", text="")
        else:
            col.prop(item, "object2", text="")
        col = row.column(align=True)
        col.prop(item, "is_collection2",
                 icon="OUTLINER_COLLECTION", icon_only=True)

        # print(data, index)
        col = row.column(align=True)
        icon = \
            "BLANK1" if len(item.results) == 0 else \
            "ERROR" if len([r for r in item.results if not r.result]) > 0 else \
            "CHECKMARK"
        op = col.operator(
            dialog.TareminPoseChecker_OT_SelectPoseDialog.bl_idname,
            text="",
            icon=icon,
        )
        for i, target in enumerate(util.get_addon_props(context).targets):
            if data == target:
                op.target_index = i
        op.test_index = index


class TareminPoseChecker_PT_Panel(bpy.types.Panel):
    bl_label = 'Taremin Pose Checker'
    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_category = 'Taremin'

    def draw_target(self, context, layout, target, target_index):
        box = layout.box()
        row = box.row(align=True)
        col = row.column(align=True)
        col.prop(
            target, "folding",
            icon="TRIA_RIGHT" if target.folding else "TRIA_DOWN",
            icon_only=True
        )

        col = row.column(align=False)
        col.prop(target, "armature", text="")
        col = row.column(align=True)
        col.prop(target, "pose_library", text="")

        col = row.column(align=False)
        op = col.operator(
            pose_checker.TareminPoseChecker_OT_RunTargetTest.bl_idname,
            text="",
            icon="PLAY",
        )
        op.target_index = target_index

        if util.get_pref(context).is_debug:
            col = row.column(align=False)
            op = col.operator(
                pose_checker.TareminPoseChecker_OT_RunTargetTestBackground.bl_idname,
                text="",
                icon="FORWARD",
            )
            op.target_index = target_index

        col = row.column(align=False)
        op = col.operator(
            pose_checker.TareminPoseChecker_OT_ResetTargetTest.bl_idname,
            text="",
            icon="REW",
        )
        op.target_index = target_index

        if target.folding:
            return

        row = box.row()
        col = row.column()
        col.template_list(
            "TareminPoseChecker_UL_UnitTestList",
            "",
            target,
            "tests",
            target,
            "test_index",
            type="DEFAULT"
        )

        col = row.column(align=True)
        col2 = col.column()
        op = col2.operator(
            unittest.TareminPoseChecker_OT_UnitTestProps_Add.bl_idname,
            text="",
            icon="ADD"
        )
        op.target_index = target_index

        col2 = col.column()
        op = col2.operator(
            unittest.TareminPoseChecker_OT_UnitTestProps_Remove.bl_idname,
            text="",
            icon="REMOVE"
        )
        op.target_index = target_index

        if len(target.tests) <= 0:
            col2.enabled = False

        row = box.row()
        row.prop(
            target, "excludes_folding",
            icon="TRIA_RIGHT" if target.excludes_folding else "TRIA_DOWN",
            text="",
            icon_only=True
        )
        row.label(
            text=util.read_resource("panel", "exclude_settings", "label"),
        )
        if not target.excludes_folding:
            row = box.row()
            col = row.column()
            col.template_list(
                "TareminPoseChecker_UL_ExcludeList",
                "",
                target,
                "excludes",
                target,
                "excludes_index",
                type="DEFAULT"
            )

        row = box.row()
        op = row.operator(
            target_props.TareminPoseChecker_OT_UnitTestTargetProps_Clear_Results.bl_idname,
            text=util.read_resource("panel", "target_clear_result", "label")
        )
        op.target_index = target_index
        op = row.operator(
            target_props.TareminPoseChecker_OT_UnitTestTargetProps_Remove.bl_idname,
            text=util.read_resource("panel", "target_remove", "label")
        )
        op.target_index = target_index

    def draw(self, context):
        settings = util.get_addon_props(context)
        layout = self.layout

        for i, target in enumerate(settings.targets):
            self.draw_target(context, layout, target, i)

        row = layout.row()
        row.operator(
            target_props.TareminPoseChecker_OT_UnitTestTargetProps_Add.bl_idname,
            text=util.read_resource("panel", "target_add", "label")
        )

        row = layout.row(align=True)
        col = row.column()
        col.operator(
            pose_checker.TareminPoseChecker_OT_RunAllTest.bl_idname,
            text=util.read_resource("panel", "run_all_tests", "label")
        )

        col = row.column(align=True)
        col.operator(
            target_props.TareminPoseChecker_OT_UnitTestTargetProps_Clear_All_Results.bl_idname,
            text=util.read_resource("panel", "clear_all_results", "label")
        )
