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
        
        # Put clavicle bones in an UI layer
        object.data.edit_bones[CLAVICLE_BONE_NAME].layers[layer_number] = True
        
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
    MCH_BODY_CHILD = 'MCH-body_child_FK'
    MCH_HEAD_SOCKET = 'MCH-head_socket_FK'
    HEAD_FK = 'head_FK'
    
    # create neck parent bone
    neck_bone = object.data.edit_bones['neck']
    head = neck_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_NECK_PARENT, 'spine02', False, head, tail, 0, 25)
    neck_parent_bone = object.data.edit_bones[MCH_NECK_PARENT]
    
    # set neck bone's parent to MCH_NECK_PARENT
    neck_bone.use_connect = False
    neck_bone.parent = neck_parent_bone
    neck_bone.layers[3] = True  # not creating another control for neck, using this bone as control
    
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
    
    # Create body child bone for head socket rig
    head = neck_bone.head.copy()
    tail = head.copy()
    tail.z += 0.07
    createNewBone(object, MCH_BODY_CHILD, 'spine02', False, head, tail, 0, 25)
    
    # create head socket bone
    head = neck_bone.head.copy()
    tail = head.copy()
    tail.z += 0.05
    createNewBone(object, MCH_HEAD_SOCKET, 'root', False, head, tail, 0, 25)
        
    # create head fk control bone, with head socket as the parent
    head = head_bone.head.copy()
    tail = head.copy()
    tail.z += 0.08
    createNewBone(object, HEAD_FK, MCH_HEAD_SOCKET, False, head, tail, 0, 3)
    
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
        MCH_BODY_CHILD)
    rotation_constraint = addCopyConstraint(object, pose_head_socket, 'COPY_ROTATION', 
        'SOCKET_ROTATION', 0.0, MCH_BODY_CHILD)
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
    pose_head_fk.custom_shape_scale = 5.0
    
    # limit transforms for control bones
    pose_neck.lock_location = [True, True, True]
    pose_neck.lock_scale = [True, True, True]
    pose_head_fk.lock_location = [True, True, True]
    pose_head_fk.lock_scale = [True, True, True]
       
def addTorsoRig(context, object, gizmo_obj):
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)
    
    # Dissolve the spine03 bone
    if 'spine03' in object.data.edit_bones:
        spine03_bone = object.data.edit_bones['spine03']
        spine03_tail = spine03_bone.tail.copy()
        object.data.edit_bones.remove(object.data.edit_bones['spine03'])
        object.data.edit_bones['spine02'].tail = spine03_tail
        
    MCH_PELVIS_PARENT = 'MCH-pelvis_parent'
    MCH_SPINE01_PARENT = 'MCH-spine01_parent'
    MCH_SPINE02_PARENT = 'MCH-spine02_parent'
    MCH_SPINE01_FK_PARENT = 'MCH-spine02_FK_parent'
    PELVIS_FK = 'pelvis_FK'
    SPINE01_FK = 'spine01_FK'
    SPINE02_FK = 'spine02_FK'    
    
    # Create parent bones for 3 torso bones
    pelvis_bone = object.data.edit_bones['pelvis']
    head = pelvis_bone.tail.copy()
    tail = head.copy()
    tail.z += 0.05
    createNewBone(object, MCH_PELVIS_PARENT, 'root', False, head, tail, 0, 25)
    pelvis_bone.use_connect = False
    pelvis_bone.parent = object.data.edit_bones[MCH_PELVIS_PARENT]
    
    spine01_bone = object.data.edit_bones['spine01']
    head = spine01_bone.head.copy()
    tail = head.copy()
    tail.z += 0.06
    createNewBone(object, MCH_SPINE01_PARENT, 'pelvis', False, head, tail, 0, 25)
    spine01_bone.use_connect = False
    spine01_bone.parent = object.data.edit_bones[MCH_SPINE01_PARENT]
    spine01_bone.use_inherit_scale = True  # We will allow scaling of chest and stomach of the body
    
    spine02_bone = object.data.edit_bones['spine02']
    head = spine02_bone.head.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, MCH_SPINE02_PARENT, 'spine01', False, head, tail, 0, 25)    
    spine02_bone.use_connect = False
    spine02_bone.parent = object.data.edit_bones[MCH_SPINE02_PARENT]
    spine02_bone.use_inherit_scale = True  # We will allow scaling of chest and stomach of the body

    # Flip the pelvis deformation bone
    pelvis_head = pelvis_bone.head.copy()
    pelvis_bone.head = pelvis_bone.tail.copy()  
    pelvis_bone.tail = pelvis_head
    
    # Create the FK control bones, with pelvis bone as parent to make sure they all move along when
    # the pelvis bone is translated
    head = pelvis_bone.tail.copy()
    tail = head.copy()
    tail.z += 0.1
    createNewBone(object, PELVIS_FK, 'root', False, head, tail, 0, 3)

    head = spine01_bone.head.copy()
    tail = head.copy()
    tail.z += 0.07
    createNewBone(object, MCH_SPINE01_FK_PARENT, 'pelvis', False, head, tail, 0, 25)    
    object.data.edit_bones[MCH_SPINE01_FK_PARENT].use_inherit_rotation = False
    
    head = spine01_bone.head.copy()
    tail = head.copy()
    tail.z += 0.08
    createNewBone(object, SPINE01_FK, MCH_SPINE01_FK_PARENT, False, head, tail, 0, 3)    

    head = spine02_bone.head.copy()
    tail = head.copy()
    tail.z += 0.12
    createNewBone(object, SPINE02_FK, 'pelvis', False, head, tail, 0, 3)
    object.data.edit_bones[SPINE02_FK].use_inherit_rotation = False
        
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # Add constraints for copy rotation/location/transforms
    pose_pelvis_parent = object.pose.bones[MCH_PELVIS_PARENT]
    addCopyConstraint(object, pose_pelvis_parent, 'COPY_ROTATION', 'FK_ROT', 1.0, PELVIS_FK)
    location_constraint = addCopyConstraint(object, pose_pelvis_parent, 'COPY_LOCATION', 'FK_LOC',
        1.0, PELVIS_FK)
    if location_constraint:
        location_constraint.owner_space = 'LOCAL'
        location_constraint.target_space = 'LOCAL'
        
    pose_spine01_parent = object.pose.bones[MCH_SPINE01_PARENT]
    addCopyConstraint(object, pose_spine01_parent, 'COPY_TRANSFORMS', 'FK', 1.0, SPINE01_FK)
    
    pose_spine01_fk_parent = object.pose.bones[MCH_SPINE01_FK_PARENT]    
    addCopyConstraint(object, pose_spine01_fk_parent, 'COPY_ROTATION', 'FK1', 1.0, PELVIS_FK)
    addCopyConstraint(object, pose_spine01_fk_parent, 'COPY_ROTATION', 'FK2', 0.5, SPINE02_FK)
    
    pose_spine02_parent = object.pose.bones[MCH_SPINE02_PARENT]
    addCopyConstraint(object, pose_spine02_parent, 'COPY_TRANSFORMS', 'FK', 1.0, SPINE02_FK)

    # Add constraints for breasts
    
    # Lock location for spine01 and spine02 FK bones
    pose_pelvis_fk = object.pose.bones[PELVIS_FK]
    pose_pelvis_fk.lock_scale = [True, True, True]
    
    pose_spine01_fk = object.pose.bones[SPINE01_FK]
    pose_spine01_fk.lock_location = [True, True, True]
    
    pose_spine02_fk = object.pose.bones[SPINE02_FK]
    pose_spine02_fk.lock_location = [True, True, True]
    
    

