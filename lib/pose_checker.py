from re import sub, template
import bpy
import bmesh
import os

from . import prop_json, subprocess, util, logging_settings


def run_target_test(context, target_index):
    target = util.get_addon_props(context).targets[target_index]
    armature = target.armature
    pose_library = target.pose_library

    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

    # save context
    current = util.get_active(context)
    current_pose_library = armature.pose_library

    exclude_dict = util.create_exclude_dict(target)

    for test_index, test in enumerate(target.tests):
        results = test.results
        results.clear()

        # skip invalid test
        if (
            not test.is_collection1 and test.object1 is None
        ) or (
            not test.is_collection2 and test.object2 is None
        ):
            continue

        collection1 = \
            [obj for obj in test.collection1.all_objects if obj.type ==
                'MESH'] if test.is_collection1 else [test.object1]
        collection2 = \
            [obj for obj in test.collection2.all_objects if obj.type ==
                'MESH'] if test.is_collection2 else [test.object2]

        if len(collection1) == 0 or len(collection2) == 0:
            continue

        for object1 in collection1:
            for object2 in collection2:
                if util.is_hide(object1) or util.is_hide(object2):
                    continue
                for i, pose in enumerate(pose_library.pose_markers):
                    # excluded
                    if util.is_excluded(exclude_dict, object1, object2, pose.name):
                        continue

                    # no pose
                    face_indices_no_pose = set(util.check_overlap(
                        context, armature, pose_library, object1, object2, pose_index=-1))

                    # posed
                    face_indices_pose = set(util.check_overlap(
                        context, armature, pose_library, object1, object2, pose_index=i))

                    diff = list(face_indices_pose - face_indices_no_pose)

                    result = results.add()
                    result.object1 = object1
                    result.object2 = object2
                    result.result = len(diff) == 0
                    result.pose_name = pose.name
                    for index1, index2 in diff:
                        f = result.faces.add()
                        f.index1 = index1
                        f.index2 = index2

    # reset transform
    util.set_active(context, armature)
    armature.pose_library = pose_library
    bpy.ops.object.mode_set(mode="POSE", toggle=False)
    bpy.ops.pose.transforms_clear()

    # restore context
    armature.pose_library = current_pose_library
    bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
    util.set_active(context, current)


class TareminPoseChecker_OT_RunAllTest(bpy.types.Operator):
    bl_idname = 'taremin.pose_checker'
    bl_label = 'TareminPoseChecker_OT_RunAllTest'
    bl_description = util.read_resource("panel", "run_all_tests", "label")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.taremin.pose_checker_run_target_test(target_index=-1)

        self.report({'INFO'}, "Complete")

        return {'FINISHED'}


class TareminPoseChecker_OT_RunTargetTestBackground(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_run_target_test_background"
    bl_label = "このBlenderプロセスで実行"
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        if self.target_index < 0:
            settings = util.get_addon_props(context)
            for target_index, target in enumerate(settings.targets):
                run_target_test(context, target_index)
        else:
            run_target_test(context, self.target_index)
        return {'FINISHED'}


class TareminPoseChecker_OT_RunTargetTest(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_run_target_test"
    bl_label = "バックグラウンドプロセスで実行"
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        logger = logging_settings.get_logger(context)
        script = os.path.join(os.path.dirname(__file__), "../background.py")
        basepath, extname = os.path.splitext(bpy.data.filepath)
        basename = bpy.path.basename(basepath)

        # exec json
        tmpfile = subprocess.exec_subprocess(script, basename, extname, options={
            "target_index": self.target_index
        })

        json_basename, json_extname = os.path.splitext(tmpfile)
        json_path = json_basename + ".json"
        logger.info(f"JSON Path: {json_path}")
        try:
            with open(json_path, "r", encoding='UTF-8') as file:
                json_str = file.read()
                prop_json.json_to_property(
                    util.get_addon_props(context), json_str)
        except Exception as e:
            logger.error(e)

        if not util.get_pref(context).is_debug:
            logger.info(f"Remove temporary files: {tmpfile}, {json_path}")
            os.remove(tmpfile)
            os.remove(json_path)
        else:
            logger.debug(f"Temporary files: {tmpfile}, {json_path}")

        return {'FINISHED'}


class TareminPoseChecker_OT_ResetTargetTest(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_reset_target_test"
    bl_label = "レストポーズに戻す"
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={'HIDDEN'})

    def execute(self, context):
        target = util.get_addon_props(context).targets[self.target_index]
        armature = target.armature

        # save context
        current = util.get_active(context)

        # cancel local view mode
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        if context.space_data.local_view:
            bpy.ops.view3d.localview()

        # reset transform
        util.set_active(context, armature)
        bpy.ops.object.mode_set(mode="POSE", toggle=False)
        bpy.ops.pose.transforms_clear()

        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        util.set_active(context, current)

        return {'FINISHED'}


class TareminPoseChecker_OT_ViewTestResult(bpy.types.Operator):
    bl_idname = 'taremin.pose_checker_view_test_result'
    bl_label = 'TareminPoseChecker_OT_ViewTestResult'
    bl_description = util.read_resource("panel", "result_pose", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(options={'HIDDEN'})
    test_index: bpy.props.IntProperty(options={'HIDDEN'})
    result_index: bpy.props.IntProperty(options={'HIDDEN'})
    mesh_only: bpy.props.BoolProperty(default=False, options={'HIDDEN'})
    edit_mode: bpy.props.BoolProperty(default=False, options={'HIDDEN'})

    @classmethod
    def description(cls, context, properties):
        if properties.mesh_only:
            if properties.edit_mode:
                return util.read_resource("panel", "result_pose_without_armature_wireframe", "label")
            else:
                return util.read_resource("panel", "result_pose_without_armature", "label")
        else:
            return util.read_resource("panel", "result_pose", "label")

    def execute(self, context):
        settings = util.get_addon_props(context)
        target = settings.targets[self.target_index]
        test = target.tests[self.test_index]
        result = test.results[self.result_index]

        if context.object.mode != "OBJECT":
            bpy.ops.object.mode_set(mode="OBJECT", toggle=False)

        # cancel local view mode
        if context.space_data.local_view:
            bpy.ops.view3d.localview()

        # check pose
        pose_library = target.pose_library
        pose_index = -1
        for i, p in enumerate(pose_library.pose_markers):
            if p.name == result.pose_name:
                pose_index = i
                break
        if pose_index < 0:
            raise ValueError("Pose not found:", result.pose_name)

        # reset transform
        armature = target.armature
        util.set_active(context, armature)
        armature.pose_library = pose_library
        bpy.ops.object.mode_set(mode="POSE", toggle=False)
        bpy.ops.pose.select_all(action="SELECT")
        bpy.ops.pose.transforms_clear()
        bpy.ops.poselib.apply_pose(pose_index=pose_index)

        object1 = result.object1
        object2 = result.object2
        bm1 = bmesh.new()
        bm1.from_mesh(object1.data)
        bm2 = bmesh.new()
        bm2.from_mesh(object2.data)

        for f in bm1.faces:
            f.select = False
        for f in bm2.faces:
            f.select = False
        for f in result.faces:
            bm1.faces.ensure_lookup_table()
            bm2.faces.ensure_lookup_table()
            bm1.faces[f.index1].select = True
            bm2.faces[f.index2].select = True

        bm1.to_mesh(object1.data)
        bm2.to_mesh(object2.data)
        bm1.free()
        bm2.free()

        # select object
        util.set_active(context, target.armature)
        bpy.ops.object.mode_set(mode="OBJECT", toggle=False)
        bpy.ops.object.select_all(action="DESELECT")
        if not self.mesh_only:
            target.armature.select_set(True)
        else:
            target.armature.select_set(False)

        object1.select_set(True)
        object2.select_set(True)
        util.set_active(context, object1)

        if self.edit_mode:
            bpy.ops.object.mode_set(mode="EDIT", toggle=False)
            bpy.context.tool_settings.mesh_select_mode = (False, False, True)
            bpy.context.space_data.shading.type = 'WIREFRAME'

        # local view mode
        bpy.ops.view3d.localview()

        return {'FINISHED'}
