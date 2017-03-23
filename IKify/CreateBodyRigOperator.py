import bpy
from .utils import createLayerArray
from .ikRig import addOneLegIK
from .fkRig import addOneFKControl

def createFKControls(context, object):
    gizmo_obj = bpy.data.objects['GZM_Circle']
    
    thigh_L_FK = addOneFKControl(context, object, 'thigh_L', gizmo_obj, 1, 1.0, 'pelvis', False)
    thigh_R_FK = addOneFKControl(context, object, 'thigh_R', gizmo_obj, 1, 1.0, 'pelvis', False)
    calf_L_FK = addOneFKControl(context, object, 'calf_L', gizmo_obj, 1, 0.8, thigh_L_FK)
    calf_R_FK = addOneFKControl(context, object, 'calf_R', gizmo_obj, 1, 0.8, thigh_R_FK)
    foot_L_FK = addOneFKControl(context, object, 'foot_L', gizmo_obj, 1, 1.5, calf_L_FK)
    foot_R_FK = addOneFKControl(context, object, 'foot_R', gizmo_obj, 1, 1.5, calf_R_FK)    
    addOneFKControl(context, object, 'toes_L', gizmo_obj, 1, 2.0, foot_L_FK)
    addOneFKControl(context, object, 'toes_R', gizmo_obj, 1, 2.0, foot_R_FK)
    
    upperarm_L_FK = addOneFKControl(context, object, 'upperarm_L', gizmo_obj, 2, 1.0, 'clavicle_L')
    upperarm_R_FK = addOneFKControl(context, object, 'upperarm_R', gizmo_obj, 2, 1.0, 'clavicle_R')
    lowerarm_L_FK = addOneFKControl(context, object, 'lowerarm_L', gizmo_obj, 2, 0.8, upperarm_L_FK)
    lowerarm_R_FK = addOneFKControl(context, object, 'lowerarm_R', gizmo_obj, 2, 0.8, upperarm_R_FK)
    addOneFKControl(context, object, 'hand_L', gizmo_obj, 2, 4.5, lowerarm_L_FK)
    addOneFKControl(context, object, 'hand_R', gizmo_obj, 2, 4.5, lowerarm_R_FK)
    
    neck_FK = addOneFKControl(context, object, 'neck', gizmo_obj, 3, 1.5, 'spine03' , False)
    addOneFKControl(context, object, 'head', gizmo_obj, 3, 2.0, neck_FK)

def createIKControls(context, object):
    addOneLegIK(context, object, 'L')
    addOneLegIK(context, object, 'R')
    
class BodyRigController(bpy.types.Operator):
    """Create the body rig"""
    bl_idname = "ikify.body_rig"
    bl_label = "Create Body Rig"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'ARMATURE'

    def execute(self, context):
        # Reset pose for all bones
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.pose.transforms_clear()
        bpy.ops.pose.select_all(action='DESELECT')
        
        # Set visibility for armature
        obj = context.active_object
        obj.show_x_ray = True
        armature = obj.data
        armature.show_bone_custom_shapes = True
        
        # Create the FK rig
        createFKControls(context, obj)
        # Create the IK rig
        createIKControls(context, obj)
        
        # Set layer visibility to only newly added controls
        bpy.ops.armature.armature_layers(layers=createLayerArray([1,2,3,4], 32))

        return {'FINISHED'}

