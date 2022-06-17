######################################################################################################
# A simple add-on that enhance the override material tool (from renderlayer panel)                   #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me                                                           #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################


############# Add-on description (used by Blender)

bl_info = {
    "name": "Material Advanced Override",
    "description": 'Material Override Tools - with advanced exclude options',
    "author": "Lapineige",
    "version": (0, 4),
    "blender": (2, 72, 0),
    "location": "Properties >",
    "warning": "",
    "wiki_url": "http://blenderlounge.fr/forum/viewtopic.php?f=26&t=810",
    "tracker_url": "http://blenderlounge.fr/forum/viewtopic.php?f=26&t=810",
    "category": "Render"}

import bpy

bpy.types.Scene.OW_only_selected = bpy.props.BoolProperty(name='Affect Only Selected',default=True)
bpy.types.Scene.OW_exclude_type = bpy.props.EnumProperty(items=[('index','Material Index','',0),('group','Group','',1),('layer','Layer','',2)])
bpy.types.Scene.OW_pass_index = bpy.props.IntProperty(name='Pass Index',default=1)
bpy.types.Scene.OW_material = bpy.props.StringProperty(name='Material',maxlen=63)
bpy.types.Scene.OW_group = bpy.props.StringProperty(name='Group',maxlen=63)

class OverwriteSetup(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "render.overwrite_setup"
    bl_label = "Overwrite Setup"
    
    l_m = []
    
    bpy.types.Scene.override_layer = bpy.props.BoolVectorProperty(subtype='LAYER', size=20)
    
    @classmethod
    def poll(cls, context):
        return context.scene.OW_material
    
    def execute(self, context):
        for obj in bpy.data.objects:
            if (
                (obj.select == True) * context.scene.OW_only_selected
                or not context.scene.OW_only_selected
            ) and len(obj.material_slots):
                if context.scene.OW_exclude_type == 'index':
                    if (
                        obj.material_slots[0].material.pass_index
                        != context.scene.OW_pass_index
                    ):
                        self.l_m.append((obj,obj.material_slots[0].material))
                        obj.material_slots[0].material = bpy.data.materials[context.scene.OW_material]
                elif context.scene.OW_exclude_type == 'group' and context.scene.OW_group:
                    if obj.name in [g_obj.name for g_obj in bpy.data.groups[context.scene.OW_group].objects]:
                        self.l_m.append((obj,obj.material_slots[0].material))
                        obj.material_slots[0].material = bpy.data.materials[context.scene.OW_material]
                elif context.scene.OW_exclude_type == 'layer':
                    if True not in [
                        (context.scene.override_layer[index])
                        * (
                            context.scene.override_layer[index]
                            == obj.layers[index]
                        )
                        for index in range(len(obj.layers))
                    ]:
                        self.l_m.append((obj,obj.material_slots[0].material))
                        obj.material_slots[0].material = bpy.data.materials[context.scene.OW_material]
        return {'FINISHED'}

class OverwriteRestore(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "render.overwrite_restore"
    bl_label = "Overwrite Restore"
    
    l_m = []

    @classmethod
    def poll(cls, context):
        return True
    
    def execute(self, context):
        for obj_mat in bpy.types.RENDER_OT_overwrite_setup.l_m:
            obj_mat[0].material_slots[0].material = obj_mat[1]
        bpy.types.RENDER_OT_overwrite_setup.l_m = []
        return {'FINISHED'}


class MaterialOverrideTools(bpy.types.Panel):
    """  """
    bl_label = "Material Override Tools"
    bl_idname = "material_override_tools"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render_layer"  
    
    def draw(self, context):
        layout = self.layout
        if bpy.types.RENDER_OT_overwrite_setup.l_m:
            layout.operator('render.overwrite_restore')
        else:
            layout.operator('render.overwrite_setup')
            layout.label('Currently not working with multiple materials per object', icon='CANCEL')
            
        
        layout.prop_search(context.scene, "OW_material", bpy.data, "materials", icon='MATERIAL_DATA')
        layout.prop(context.scene, 'OW_only_selected',toggle=True, icon='BORDER_RECT')
        
        box = layout.box()
        box.label('Exclude from effect:')
        row = box.row()
        row.prop(context.scene, 'OW_exclude_type', expand=True)
        if context.scene.OW_exclude_type == 'index':
            box.prop(context.scene, 'OW_pass_index')
        elif context.scene.OW_exclude_type == 'group':
            box.prop_search(context.scene, "OW_group", bpy.data, "groups", icon='GROUP')
        elif context.scene.OW_exclude_type == 'layer':
            box.prop(context.scene, 'override_layer', text='')
                

def register():
    bpy.utils.register_class(OverwriteSetup)
    bpy.utils.register_class(OverwriteRestore)
    bpy.utils.register_class(MaterialOverrideTools)


def unregister():
    bpy.utils.unregister_class(OverwriteSetup)
    bpy.utils.unregister_class(OverwriteRestore)
    bpy.utils.unregister_class(MaterialOverrideTools)


if __name__ == "__main__":
    register()
