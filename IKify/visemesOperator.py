import bpy

def copyVertexGroups(source_obj, dest_obj, vgroup_names):
    vgroup_ids = {}
    for name in vgroup_names:
        dest_obj.vertex_groups.new(name)
        vgroup_ids[source_obj.vertex_groups[name].index] = name
        
    for i, v in enumerate(source_obj.data.vertices):
        for source_vgroup in v.groups:
            if source_vgroup.group in vgroup_ids:
                dest_vgroup = dest_obj.vertex_groups[vgroup_ids[source_vgroup.group]]
                dest_vgroup.add([i], source_vgroup.weight, 'ADD')

class VisemesOperator(bpy.types.Operator):
    """Create all the Visemes Shape Keys"""
    bl_idname = "object.create_visemes"
    bl_label = "Create Visemes shapekeys"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def execute(self, context):
        scene = context.scene
        reference_obj = scene.objects['IKify_reference_mesh_human_female']

        # Copy LowerMouth and UpperMouth vertex groups
        bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        copyVertexGroups(reference_obj, context.active_object, ['LowerMouth', 'UpperMouth'])
        return {'FINISHED'}


def register():
    bpy.utils.register_class(VisemesOperator)


def unregister():
    bpy.utils.unregister_class(VisemesOperator)


if __name__ == "__main__":
    register()