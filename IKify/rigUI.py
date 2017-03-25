import bpy

class IkifyRigPanel(bpy.types.Panel):
    """Creates a Panel for IKify Rig UI"""
    bl_label = "IKify Rig UI"
    bl_idname = "IKify_rig_ui"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Ikify Rig'
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'POSE'

    def draw(self, context):
        layout = self.layout

        obj = context.object

        row = layout.row()
        row.label("")
        row.label("Left")
        row.label("Right")
        
        layout.label("IK Influence")
        row = layout.row()
        row.label("Arm")
        row.prop(obj, 'ArmIk_L', text="")
        row.prop(obj, 'ArmIk_R', text="")
        row = layout.row()
        row.label("Leg")
        row.prop(obj, 'LegIk_L', text="")
        row.prop(obj, 'LegIk_R', text="")
        
        layout.label("Constrain Rotation")
        row = layout.row()
        row.label("Arm")
        row.prop(obj, 'ArmRotationIk_L', text="")
        row.prop(obj, 'ArmRotationIk_R', text="")
