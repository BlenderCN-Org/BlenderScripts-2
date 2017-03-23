import bpy
from .utils import *
    
def addOneLegIK(context, object, L_R):    
    # create copies of thigh and calf bones
    copyDeformationBone(object, 'thigh_' + L_R + '_IK', 'thigh_' + L_R, 'pelvis', False, 24)
    copyDeformationBone(object, 'calf_' + L_R + '_IK', 'calf_' + L_R, 'thigh_' + L_R + '_IK', True, 24)    
    copyDeformationBone(object, 'foot_' + L_R + '_IK', 'foot_' + L_R, 'root', False, 4)    

    bpy.ops.object.mode_set(mode='EDIT', toggle=False)        
    
    # Create knee target IK control bone
    calf = object.data.edit_bones['calf_' + L_R]
    head = calf.head.copy()  # knee position
    head.y -= 0.7
    tail = head.copy()
    tail.y -= 0.1
    createNewBone(object, 'knee_target_' + L_R + '_IK', 'foot_' + L_R + '_IK', False, head, tail, 0, 4)
        
    # Switch to pose mode to add all the constraints
    bpy.ops.object.mode_set(mode='POSE', toggle=False)
    
    # first, set copy rotation constraints on deformation bones, to copy IK bones' rotations
    # also add drivers for FK --> IK Control
    pose_thigh = object.pose.bones['thigh_' + L_R]
    constraint = addCopyConstraint(object, pose_thigh, 'COPY_ROTATION', 'IK', 0.0,
        'thigh_' + L_R + '_IK')
    addDriver(constraint, 'influence', object, '["LegIk_' + L_R + '"]')
    
    pose_calf = object.pose.bones['calf_' + L_R]
    constraint = addCopyConstraint(object, pose_calf, 'COPY_ROTATION', 'IK', 0.0,
        'calf_' + L_R + '_IK')
    addDriver(constraint, 'influence', object, '["LegIk_' + L_R + '"]')
    
    pose_foot = object.pose.bones['foot_' + L_R]
    constraint = addCopyConstraint(object, pose_foot, 'COPY_ROTATION', 'IK', 0.0,
        'foot_' + L_R + '_IK')
    addDriver(constraint, 'influence', object, '["LegIk_' + L_R + '"]')

    # next, add the IK constraint itself
    pose_calf_IK = object.pose.bones['calf_' + L_R + '_IK']
    if 'IK' not in pose_calf_IK.constraints:
        constraint = pose_calf_IK.constraints.new('IK')
        constraint.name = 'IK'
        constraint.influence = 1.0
        constraint.target = object
        constraint.subtarget = 'foot_' + L_R + '_IK'
        constraint.pole_target = object
        constraint.pole_subtarget = 'knee_target_' + L_R + '_IK'
        constraint.pole_angle = 3.14159 / 2.0  # 90 degrees in radians
        constraint.chain_count = 2
        pose_calf_IK.lock_ik_y = True
        pose_calf_IK.lock_ik_z = True
