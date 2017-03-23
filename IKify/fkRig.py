import bpy
from .utils import *

def addOneFKControl(context, object, deform_bone_name, gizmo_obj, layer_number, scale, 
    new_bone_parent, parent_connected = True):    
    # Make sure we are in pose mode
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    # If a bone with the same name as new FK control bone already exists,
    # return
    new_bone_name = deform_bone_name + "_FK"
    if new_bone_name in object.data.edit_bones:
        return new_bone_name
    
    copyDeformationBone(object, new_bone_name, deform_bone_name, new_bone_parent, 
        parent_connected, layer_number)
    
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    pose_bone = object.pose.bones[deform_bone_name]
    new_bone = object.pose.bones[new_bone_name]    

    # Set the custom shape
    new_bone.custom_shape = gizmo_obj
    new_bone.use_custom_shape_bone_size = True
    new_bone.custom_shape_scale = scale
    
    # Apply copy transforms constraint
    constraint = addCopyConstraint(object, pose_bone, 'COPY_ROTATION', 'FK', 1.0, new_bone_name)
    
    # add driver
    if (deform_bone_name.startswith('thigh') or deform_bone_name.startswith('calf') or
        deform_bone_name.startswith('foot') or deform_bone_name.startswith('toes')):
        L_R = deform_bone_name[-1]
        addDriver(constraint, 'influence', object, '["LegIk_' + L_R + '"]', True)
    
    return new_bone_name
