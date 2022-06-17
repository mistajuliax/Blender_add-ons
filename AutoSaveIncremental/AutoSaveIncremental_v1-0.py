######################################################################################################
# An operator to automatically save your file with an incremental suffix                             #
# Actualy partly uncommented - if you do not understand some parts of the code,                      #
# please see further version or contact me.                                                          #
# Author: Lapineige                                                                                  #
# License: GPL v3                                                                                    #
######################################################################################################

############# Add-on description (used by Blender)

bl_info = {
    "name": "Auto Save Incremental",
    "description": 'Automatically save your file with an incremental suffix (after a defined period of time)',
    "author": "Lapineige",
    "version": (1, 0),
    "blender": (2, 74, 0),
    "location": "Search > Auto Save Incremental",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "System"}

##############

import bpy, os
from time import time as tm
from bpy.props import IntProperty, FloatProperty

##############

def detect_number(name):
    last_nb_index = -1

    for i in range(1,len(name)):
        if name[-i].isnumeric():
            if last_nb_index == -1:
                last_nb_index = len(name)-i+1 # +1 because last index in [:] need to be 1 more
        elif last_nb_index != -1:
            first_nb_index = len(name)-i+1 #+1 to restore previous index
            return (first_nb_index,last_nb_index,name[first_nb_index:last_nb_index]) #first: index of the number / last: last number index +1
    return False

class FileIncrementalSave(bpy.types.Operator):
    bl_idname = "file.save_incremental"
    bl_label = "Save Incremental"
   
    def execute(self, context):
        if bpy.data.filepath:
            f_path = bpy.data.filepath
            #bpy.ops.wm.save_mainfile(filepath=f_path)

            increment_files=[file for file in os.listdir(os.path.dirname(f_path)) if os.path.basename(f_path).split('.blend')[0] in file.split('.blend')[0] and file.split('.blend')[0] !=  os.path.basename(f_path).split('.blend')[0]]
            for file in increment_files:
                if not detect_number(file):
                    increment_files.remove(file)
            numbers_index = [ ( index, detect_number(file.split('.blend')[0]) ) for index, file in enumerate(increment_files)]
            if numbers := [index_nb[1] for index_nb in numbers_index]:
                str_nb = str(max(int(n[2]) for n in numbers) + 1)

            if increment_files:
                d_nb = detect_number(increment_files[-1].split('.blend')[0])
                str_nb = str_nb.zfill(len(d_nb[2]))
                #print(d_nb, len(d_nb[2]))
            else:
                d_nb =False
                d_nb_filepath = detect_number(os.path.basename(f_path).split('.blend')[0])
                #if numbers: ## USELESS ??
                #    str_nb.zfill(3)
                if d_nb_filepath:
                    str_nb = str(int(d_nb_filepath[2]) + 1).zfill(len(d_nb_filepath[2]))

            if d_nb:
                output = (
                    bpy.path.abspath("//")
                    + increment_files[-1].split('.blend')[0][: d_nb[0]]
                    + str_nb
                    + '.blend'
                    if len(increment_files[-1].split('.blend')[0]) < d_nb[1]
                    else bpy.path.abspath("//")
                    + increment_files[-1].split('.blend')[0][: d_nb[0]]
                    + str_nb
                    + increment_files[-1].split('.blend')[0][d_nb[1] :]
                    + '.blend'
                )

            elif d_nb_filepath:
                if len(os.path.basename(f_path).split('.blend')[0]) < d_nb_filepath[1]: # in case last_nb_index is just after filename's max index
                    output = bpy.path.abspath("//") + os.path.basename(f_path).split('.blend')[0][:d_nb_filepath[0]] + str_nb + '.blend'
                else:
                    output = bpy.path.abspath("//") + os.path.basename(f_path).split('.blend')[0][:d_nb_filepath[0]] + str_nb + os.path.basename(f_path).split('.blend')[0][d_nb_filepath[1]:] + '.blend'
            else:
                output = f_path.split(".blend")[0] + '_' + '001' + '.blend'

            if os.path.isfile(output):
                self.report({'WARNING'}, "Internal Error: trying to save over an existing file. Cancelled")
                print('Tested Output: ', output)
                return {'CANCELLED'}
            bpy.ops.wm.save_mainfile()
            bpy.ops.wm.save_as_mainfile(filepath=output, copy=True)

            self.report({'INFO'}, "File: {0} - Created at: {1}".format(output[len(bpy.path.abspath("//")):], output[:len(bpy.path.abspath("//"))]))
        else:
            self.report({'WARNING'}, "Please save a main file")
        return {'FINISHED'}
        ###### PENSER A TESTER AUTRES FICHIERS DU DOSSIER, VOIR SI TROU DANS NUMEROTATION==> WARNING

class ModalOperator(bpy.types.Operator):
    """Move an object with the mouse, example"""
    bl_idname = "object.modal_operator"
    bl_label = "Auto Save Incremental"
    
    def modal(self, context, event):
        #print(tm()-self.time)
        if event.type=="ESC":
            return {'FINISHED'}
        if tm()-self.time >= 30:
            print('Auto Saving...')
            bpy.ops.file.save_incremental()
            self.time = tm()
            
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self.time = tm()
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
        #self.report({'WARNING'}, "No active object, could not finish")
        #return {'CANCELLED'}


def draw_into_file_menu(self,context):
    self.layout.operator('file.save_incremental', icon='SAVE_COPY')


def register():
    bpy.utils.register_class(FileIncrementalSave)
    bpy.types.INFO_MT_file.prepend(draw_into_file_menu)
    bpy.utils.register_class(ModalOperator)


def unregister():
    bpy.utils.unregister_class(FileIncrementalSave)
    bpy.types.INFO_MT_file.remove(draw_into_file_menu)
    bpy.utils.unregister_class(ModalOperator)


if __name__ == "__main__":
    register()
