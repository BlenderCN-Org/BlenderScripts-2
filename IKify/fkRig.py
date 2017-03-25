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
    
    # In case of the upper arm bone, create the arm socket bone.
    L_R = deform_bone_name[-1]
    MCH_CLAVICLE_CHILD = 'MCH-clavicle_child_' + L_R + '_FK'
    MCH_ARM_SOCKET = 'MCH-arm_socket_' + L_R + '_FK'
    CLAVICLE_BONE_NAME = 'clavicle_' + L_R
    if deform_bone_name.startswith('upperarm'):
        # Create the clavicle child bone
        clavicle = object.data.edit_bones[CLAVICLE_BONE_NAME]       
        head = clavicle.tail.copy()
        tail = head.copy()
        tail.z += 0.1
        createNewBone(object, MCH_CLAVICLE_CHILD, CLAVICLE_BONE_NAME, False, head, tail, 0, 25)
        
        # Create the arm socket bone        
        head = clavicle.tail.copy()
        tail = head.copy()
        tail.z += 0.05
        createNewBone(object, MCH_ARM_SOCKET, 'root', False, head, tail, 0, 25)
        new_bone_parent = MCH_ARM_SOCKET
        parent_connected = False
        
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
    
    # add driver for leg FK --> IK control
    if (deform_bone_name.startswith('thigh') or deform_bone_name.startswith('calf') or
        deform_bone_name.startswith('foot') or deform_bone_name.startswith('toes')):
        L_R = deform_bone_name[-1]
        addDriver(constraint, 'influence', object, '["LegIk_' + L_R + '"]', True)

    # add driver for arm FK --> IK control
    if (deform_bone_name.startswith('upperarm') or deform_bone_name.startswith('lowerarm') or
        deform_bone_name.startswith('hand')):
        L_R = deform_bone_name[-1]
        addDriver(constraint, 'influence', object, '["ArmIk_' + L_R + '"]', True)
        
    # add constraints and a driver for arm socket rig
    if deform_bone_name.startswith('upperarm'):
        pose_socket_bone = object.pose.bones[MCH_ARM_SOCKET]
        addCopyConstraint(object, pose_socket_bone, 'COPY_LOCATION', 'SOCKET_LOCATION', 1.0, 
            MCH_CLAVICLE_CHILD)
        
        rotation_constraint = addCopyConstraint(object, pose_socket_bone, 'COPY_ROTATION',
            'SOCKET_ROTATION', 0.0, MCH_CLAVICLE_CHILD)
        addDriver(rotation_constraint, 'influence', object, '["ArmRotationIk_' + L_R + '"]')
        
        # lock upper arm transforms
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_location = [True, True, True]

    # lock some transforms for various bones
    if deform_bone_name.startswith('lowerarm'):
        new_bone.rotation_mode = 'XYZ'
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_rotation = [False, True, True]
        
    if deform_bone_name.startswith('thigh'):
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_location = [True, True, True]
        
    if deform_bone_name.startswith('calf'):
        new_bone.rotation_mode = 'XYZ'
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_rotation = [False, True, True]

    if deform_bone_name.startswith('toes'):
        new_bone.rotation_mode = 'YZX'
        new_bone.lock_scale = [True, True, True]
        new_bone.lock_rotation = [False, True, True]
        
    return new_bone_name
