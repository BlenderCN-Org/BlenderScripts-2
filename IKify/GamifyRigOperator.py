import bpy

def copyVertexGroup(object, source_group, dest_group):
    if source_group not in object.vertex_groups or dest_group not in object.vertex_groups:
        return
        
    source_vgroup_id = object.vertex_groups[source_group].index
    dest_vgroup = object.vertex_groups[dest_group]
        
    for i, v in enumerate(object.data.vertices):
        for vgroup in v.groups:
            if vgroup.group == source_vgroup_id:
               dest_vgroup.add([i], vgroup.weight, 'ADD')


class GamifyRigOperator(bpy.types.Operator):
    """Modify vertex painting for Game Engines"""
    bl_idname = "ikify.gamify_rig"
    bl_label = "Setup Rig for Game Engines"
    bl_options = {'UNDO', 'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.active_object is not None and context.active_object.type == 'MESH'

    def execute(self, context):
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        object = context.active_object
        
        # For torso
        copyVertexGroup(object, 'spine03', 'spine02')
        
        # For Hands
        for L_R in ['L', 'R']:
            copyVertexGroup(object, 'index00_' + L_R, 'index01_' + L_R)
            copyVertexGroup(object, 'middle00_' + L_R, 'middle01_' + L_R)
            copyVertexGroup(object, 'ring00_' + L_R, 'ring01_' + L_R)
            copyVertexGroup(object, 'pinky00_' + L_R, 'pinky01_' + L_R)
        
        return {'FINISHED'}