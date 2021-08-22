import bpy
import bmesh
import json
import os
from mathutils.bvhtree import BVHTree

path = os.path.join(os.path.dirname(__file__), "../resources.json")
resources = json.load(open(path, encoding="utf-8"))


def get_addon_name():
    return __package__.split('.', 2)[0]


def get_pref(context):
    return context.preferences.addons[get_addon_name()].preferences


def set_active(context, obj):
    context.window.view_layer.objects.active = obj


def get_active(context):
    return context.window.view_layer.objects.active


def get_addon_props(context):
    return context.scene.taremin_pc


def is_hide(obj):
    return obj.hide_viewport or not obj.visible_get()


def read_resource(*props):
    lang = bpy.app.translations.locale
    prop = resources
    for prop_name in props:
        prop = prop[prop_name]
    return prop[lang] if lang in prop else prop["en_US"]


def check_overlap(context, armature, pose_library, object1, object2, pose_index):
    # reset transform
    set_active(context, armature)
    armature.pose_library = pose_library
    bpy.ops.object.mode_set(mode="POSE", toggle=False)
    bpy.ops.pose.select_all(action="SELECT")
    for bone in armature.data.bones:
        bone.select = True
    bpy.ops.pose.transforms_clear()
    if pose_index >= 0:
        bpy.ops.poselib.apply_pose(pose_index=pose_index)

    # create duplicated obejct1, object2
    object1_dup = prepare_object(context, object1)
    object2_dup = prepare_object(context, object2)

    # check overlap
    face_indices = get_overlap_face_indices(
        object1_dup, object2_dup)

    # remove duplicated object1, object2
    objs = bpy.data.objects
    objs.remove(object1_dup, do_unlink=True)
    objs.remove(object2_dup, do_unlink=True)

    return face_indices


def prepare_object(context, obj):
    # duplicate object
    obj_dup = obj.copy()
    obj_dup.data = obj.data.copy()
    context.collection.objects.link(obj_dup)

    # remove all shapekeys
    if obj_dup.data.shape_keys is not None:
        for k in obj_dup.data.shape_keys.key_blocks:
            obj_dup.shape_key_remove(k)

    # remove modifier
    set_active(context, obj_dup)
    for m in obj_dup.modifiers:
        if m.type == 'ARMATURE':
            bpy.ops.object.modifier_apply(modifier=m.name)
    obj_dup.modifiers.clear()

    return obj_dup


def get_overlap_face_indices(obj1, obj2):
    bm1 = bmesh.new()
    bm1.from_mesh(obj1.data)
    bm1.transform(obj1.matrix_world)

    bm2 = bmesh.new()
    bm2.from_mesh(obj2.data)
    bm2.transform(obj2.matrix_world)

    Tree_obj1 = BVHTree.FromBMesh(bm1, epsilon=0)
    Tree_obj2 = BVHTree.FromBMesh(bm2, epsilon=0)

    overlap_pairs = Tree_obj1.overlap(Tree_obj2)

    bm1.free()
    bm2.free()

    return overlap_pairs


def create_exclude_dict(target):
    exclude_dict = {}

    for ex in target.excludes:
        tmp = [ex.object1.name, ex.object2.name]
        tmp.sort()
        tmp.append(ex.pose_name)
        exclude_dict['\0'.join(tmp)] = True

    return exclude_dict


def is_excluded(exclude_dict, object1, object2, pose_name):
    tmp = [object1.name, object2.name]
    tmp.sort()
    tmp.append(pose_name)
    key = '\0'.join(tmp)
    return (key in exclude_dict)
