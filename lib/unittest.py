import bpy
from . import result, util


def update(self, context, object, collection, is_collection):
    if getattr(self, is_collection):
        setattr(self, object, None)
    else:
        setattr(self, collection, None)


class TareminPoseCheckerUnitTestProps(bpy.types.PropertyGroup):
    object1: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=lambda self, obj: obj.type == 'MESH')
    object2: bpy.props.PointerProperty(
        type=bpy.types.Object, poll=lambda self, obj: obj.type == 'MESH')
    is_collection1: bpy.props.BoolProperty(
        default=False,
        update=lambda self, context: update(
            self, context, "object1", "collection1", "is_collection1"),
    )
    is_collection2: bpy.props.BoolProperty(
        default=False,
        update=lambda self, context: update(
            self, context, "object2", "collection2", "is_collection2"),
    )
    collection1: bpy.props.PointerProperty(
        type=bpy.types.Collection
    )
    collection2: bpy.props.PointerProperty(
        type=bpy.types.Collection
    )
    results: bpy.props.CollectionProperty(
        type=result.TareminPoseCheckerUnitTestResultProps)


class TareminPoseChecker_OT_UnitTestProps_Add(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_test_add"
    bl_label = "Add Test Entry"
    bl_description = util.read_resource("panel", "unittest_add", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(default=0, options={'HIDDEN'})

    def execute(self, context):
        settings = context.scene.taremin_pc.targets[self.target_index]

        settings.tests.add()
        settings.test_index = len(settings.tests) - 1

        return {'FINISHED'}


class TareminPoseChecker_OT_UnitTestProps_Remove(bpy.types.Operator):
    bl_idname = "taremin.pose_checker_test_remove"
    bl_label = "Remove Test Entry"
    bl_description = util.read_resource("panel", "unittest_remove", "label")
    bl_options = {'REGISTER', 'UNDO'}

    target_index: bpy.props.IntProperty(default=0, options={'HIDDEN'})

    def execute(self, context):
        settings = context.scene.taremin_pc.targets[self.target_index]

        settings.tests.remove(settings.test_index)
        max_index = len(settings.tests) - 1

        if settings.test_index > max_index:
            settings.test_index = max_index

        return {'FINISHED'}
