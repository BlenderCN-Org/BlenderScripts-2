import bpy

class FKControlsOperator(bpy.types.Operator):
    """Create all the FK controls for the bones"""
    bl_idname = "object.create_visemes"
    bl_label = "Create Visemes shapekeys"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        
        # Set pose mode
        bpy.ops.object.mode_set(mode='POSE', toggle=False)
        
        armature = context.active_object.data
        armature.show_bone_custom_shapes = True
        


        return {'FINISHED'}


def register():
    bpy.utils.register_class(FKControlsOperator)


def unregister():
    bpy.utils.unregister_class(FKControlsOperator)


if __name__ == "__main__":
    register()