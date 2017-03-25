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
        if rotation_constraint:
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
    
def addHeadNeckRig(context, object, gizmo_obj):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)       

    MCH_NECK_PARENT = 'MCH-neck_parent_FK'
    MCH_HEAD_PARENT = 'MCH-head_parent_FK'
    MCH_NECK_CHILD = 'MCH-neck_child_FK'
    MCH_HEAD_SOCKET = 'MCH-head_socket_FK'
    HEAD_FK = 'head_FK'
    
    # create neck parent bone
    neck_bone = object.data.edit_bones['neck']
    head = neck_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_NECK_PARENT, 'spine03', False, head, tail, 0, 25)
    neck_parent_bone = object.data.edit_bones[MCH_NECK_PARENT]
    
    # set neck bone's parent to MCH_NECK_PARENT
    neck_bone.use_connect = False
    neck_bone.parent = neck_parent_bone
    neck_bone.layers[3] = True  # not creating another control for neck, using this bone as control
    
    # Create neck child bone for head socket rig
    head = neck_bone.tail.copy()
    tail = head.copy()
    tail.z += 0.07
    createNewBone(object, MCH_NECK_CHILD, 'neck', True, head, tail, 0, 25)

    # create head parent bone
    head_bone = object.data.edit_bones['head']
    head = head_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_HEAD_PARENT, 'neck', True, head, tail, 0, 25)
    head_parent_bone = object.data.edit_bones[MCH_HEAD_PARENT]
    
    # set head bone's parent to MCH_HEAD_PARENT
    head_bone.use_connect = False
    head_bone.parent = head_parent_bone
    
    # create head socket bone
    head = head_bone.head.copy()
    tail = head.copy()
    tail.z += 0.05
    head_fk_bone = createNewBone(object, MCH_HEAD_SOCKET, 'root', False, head, tail, 0, 25)
        
    # create head fk control bone, with head socket as the parent
    head = head_bone.head.copy()
    tail = head.copy()
    tail.z += 0.08
    head_fk_bone = createNewBone(object, HEAD_FK, MCH_HEAD_SOCKET, False, head, tail, 0, 3)
    
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # add copy rotation constraints for neck and head parents
    pose_neck_parent = object.pose.bones[MCH_NECK_PARENT]
    # this has influence of 0.5 so that it follows head rotation half way
    addCopyConstraint(object, pose_neck_parent, 'COPY_ROTATION', 'FK', 0.5, HEAD_FK)
    
    pose_head_parent = object.pose.bones[MCH_HEAD_PARENT]
    addCopyConstraint(object, pose_head_parent, 'COPY_ROTATION', 'FK', 1.0, HEAD_FK)
    
    # create constraints for head socket
    pose_head_socket = object.pose.bones[MCH_HEAD_SOCKET]
    addCopyConstraint(object, pose_head_socket, 'COPY_LOCATION', 'SOCKET_LOCATION', 1.0, 
        MCH_NECK_CHILD)
    rotation_constraint = addCopyConstraint(object, pose_head_socket, 'COPY_ROTATION', 
        'SOCKET_ROTATION', 0.0, MCH_NECK_CHILD)
    if rotation_constraint:
        addDriver(rotation_constraint, 'influence', object, '["HeadRotationIk"]')
        
    # add custom shapes for neck and head fk bones
    pose_neck = object.pose.bones['neck']
    pose_neck.custom_shape = gizmo_obj
    pose_neck.use_custom_shape_bone_size = True
    pose_neck.custom_shape_scale = 1.5
    
    pose_head_fk = object.pose.bones[HEAD_FK]
    pose_head_fk.custom_shape = gizmo_obj
    pose_head_fk.use_custom_shape_bone_size = True
    pose_head_fk.custom_shape_scale = 4.0
    
    # limit transforms for control bones
    pose_neck.lock_location = [True, True, True]
    pose_neck.lock_scale = [True, True, True]
    pose_head_fk.lock_location = [True, True, True]
    pose_head_fk.lock_scale = [True, True, True]
    

    
    
    

