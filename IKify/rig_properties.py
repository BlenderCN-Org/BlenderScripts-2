import bpy

def add_properties():
    bpy.types.Object.LegIk_L = bpy.props.FloatProperty(name='LegIk_L', default=0.0, min=0.0, 
        max=1.0)
    bpy.types.Object.LegIk_R = bpy.props.FloatProperty(name='LegIk_R', default=0.0, min=0.0, 
        max=1.0)