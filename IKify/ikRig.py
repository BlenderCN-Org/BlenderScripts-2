import bpy
from .utils import *
    
def addOneLegIK(context, object, L_R):    
    # create all the bones we need. These are created in a topologically sorted manner,
    # so that parents can be set correctly during creation of bones themselves.
    # MCH bones are mechanism bones which will be hidden from the user
    
    MCH_THIGH = 'MCH-thigh_' + L_R + '_IK'
    MCH_CALF = 'MCH-calf_' + L_R + '_IK'
    MCH_FOOT = 'MCH-foot_' + L_R + '_IK'
    MCH_FOOT_ROLL_PARENT = 'MCH-foot_roll_parent_' + L_R + '_IK'
    MCH_FOOT_ROCKER = 'MCH-foot_rocker_' + L_R + '_IK'
    FOOT_IK = 'foot_' + L_R + '_IK'
    TOES_IK = 'toes_' + L_R + '_IK'
    FOOT_ROLL_IK = 'foot_roll_' + L_R + '_IK'
    KNEE_TARGET_IK = 'knee_target_' + L_R + '_IK'
    
    PI = 3.14159
    
    bpy.ops.object.mode_set(mode='EDIT', toggle=False)

    copyDeformationBone(object, MCH_THIGH, 'thigh_' + L_R, 'pelvis', False, 24)
    copyDeformationBone(object, MCH_CALF, 'calf_' + L_R, MCH_THIGH, True, 24)    
    copyDeformationBone(object, FOOT_IK, 'foot_' + L_R, 'root', False, 4)
    
    # Create the foot roll parent
    foot = object.data.edit_bones['foot_' + L_R]
    head = foot.tail.copy()
    tail = foot.head.copy()
    head.y = tail.y
    createNewBone(object, MCH_FOOT_ROLL_PARENT, FOOT_IK, False, head, tail, 0, 24)
    
    # Create the foot rocker Bone
    foot = object.data.edit_bones['foot_' + L_R]
    head = foot.tail.copy()
    tail = foot.head.copy()
    tail.z = head.z
    createNewBone(object, MCH_FOOT_ROCKER,  MCH_FOOT_ROLL_PARENT, False, head, tail, 0, 24)
    
    copyDeformationBone(object, MCH_FOOT, 'foot_' + L_R, MCH_FOOT_ROCKER, False, 24)    
    copyDeformationBone(object, TOES_IK, 'toes_' + L_R, MCH_FOOT_ROLL_PARENT, False, 4)

    # Create the foot roll control
    head = foot.tail.copy()
    head.y += 0.2
    tail = head.copy()
    tail.z += 0.08
    tail.y += 0.02
    createNewBone(object, FOOT_ROLL_IK, FOOT_IK, False, head, tail, 0, 4)
        
    # Create knee target IK control bone
    calf = object.data.edit_bones['calf_' + L_R]
    head = calf.head.copy()  # knee position
    head.y -= 0.7
    tail = head.copy()
    tail.y -= 0.1
    createNewBone(object, KNEE_TARGET_IK, MCH_FOOT, False, head, tail, 0, 4)
    
    # Switch to pose mode to add all the constraints
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # first, set copy rotation constraints on deformation bones, to copy IK bones' rotations
    # also add drivers for FK --> IK Control
    DRIVER_TARGET = '["LegIk_' + L_R + '"]'
    
    pose_thigh = object.pose.bones['thigh_' + L_R]
    constraint = addCopyConstraint(object, pose_thigh, 'COPY_ROTATION', 'IK', 0.0, MCH_THIGH)
    addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_calf = object.pose.bones['calf_' + L_R]
    constraint = addCopyConstraint(object, pose_calf, 'COPY_ROTATION', 'IK', 0.0, MCH_CALF)
    addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    pose_foot = object.pose.bones['foot_' + L_R]
    constraint = addCopyConstraint(object, pose_foot, 'COPY_ROTATION', 'IK', 0.0, MCH_FOOT)
    addDriver(constraint, 'influence', object, DRIVER_TARGET)

    pose_toes = object.pose.bones['toes_' + L_R]
    constraint = addCopyConstraint(object, pose_toes, 'COPY_ROTATION', 'IK', 0.0, TOES_IK)
    addDriver(constraint, 'influence', object, DRIVER_TARGET)
    
    # next, add the IK constraint itself
    pose_calf_IK = object.pose.bones[MCH_CALF]
    if 'IK' not in pose_calf_IK.constraints:
        constraint = pose_calf_IK.constraints.new('IK')
        constraint.name = 'IK'
        constraint.influence = 1.0
        constraint.target = object
        constraint.subtarget = MCH_FOOT
        constraint.pole_target = object
        constraint.pole_subtarget = KNEE_TARGET_IK
        constraint.pole_angle = PI / 2.0
        constraint.chain_count = 2
        pose_calf_IK.lock_ik_y = True
        pose_calf_IK.lock_ik_z = True

    # Create the foot roll mechanism
    pose_mch_foot_rocker = object.pose.bones[MCH_FOOT_ROCKER]
    copyConstraint = addCopyConstraint(object, pose_mch_foot_rocker, 'COPY_ROTATION', 'FOOT_ROLL',
        1.0, FOOT_ROLL_IK)
    copyConstraint.owner_space = 'LOCAL'
    copyConstraint.target_space = 'LOCAL'
    
    limitConstraint = addLimitConstraint(pose_mch_foot_rocker, 'LIMIT_ROTATION', 'FOOT_ROLL_LIMIT',
        1.0, [True, 0, PI / 2.0])
    limitConstraint.owner_space = 'LOCAL'
    
    pose_foot_roll_parent = object.pose.bones[MCH_FOOT_ROLL_PARENT]
    copyConstraint = addCopyConstraint(object, pose_foot_roll_parent, 'COPY_ROTATION', 'FOOT_ROLL',
        1.0, FOOT_ROLL_IK)
    copyConstraint.owner_space = 'LOCAL'
    copyConstraint.target_space = 'LOCAL'
    
    limitConstraint = addLimitConstraint(pose_foot_roll_parent, 'LIMIT_ROTATION', 'FOOT_ROLL_LIMIT',
        1.0, [True, -1.0 * (PI / 2.0), 0])
    limitConstraint.owner_space = 'LOCAL'
    
    # Limit transformations
    pose_foot_roll = object.pose.bones[FOOT_ROLL_IK]
    pose_foot_roll.rotation_mode = 'XYZ'
    pose_foot_roll.lock_scale = [True, True, True]
    pose_foot_roll.lock_location = [True, True, True]
    pose_foot_roll.lock_rotation = [False, True, True]
        
    pose_toes_IK = object.pose.bones[TOES_IK]
    pose_toes_IK.rotation_mode = 'YZX'
    pose_toes_IK.lock_scale = [True, True, True]
    pose_toes_IK.lock_location = [True, True, True]
    pose_toes_IK.lock_rotation = [False, True, True]
