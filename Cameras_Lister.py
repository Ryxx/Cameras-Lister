# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

bl_info = {
    "name": "Cameras Lister",
    "author": "Ryxx",
    "blender": (2, 80, 0),
    "description": "Lists all cameras from the scene and allows to easily set the view to a particular one.",
    "location": "Camera Lister Panel shortcut: Alt + C",
    "support": "COMMUNITY",
    "category": "Camera"
}

import bpy
from bpy.types import Menu

#--------------------------------------------------------------------------------------
# F U N C T I O N A L I T I E S
#--------------------------------------------------------------------------------------

# SORTING CAMERAS OPTIONS
sorting_cameras_options = [
        ("alphabetically", "Alphabetically", ""),
        ("by_collections", "By Collections", "")]

bpy.types.Scene.sort_cameras = bpy.props.EnumProperty(
    items=sorting_cameras_options,
    description="Sort cameras",
    default= "alphabetically")

class SetCameraView(bpy.types.Operator):
    bl_idname = 'cameras.set_view'
    bl_label = 'Set Camera View'
    bl_description = "Set View to this Camera"
    bl_options = {'REGISTER', 'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        bpy.ops.cameras.select(camera=self.camera)
        bpy.ops.view3d.object_as_camera()

        return{'FINISHED'}

class SelectCamera(bpy.types.Operator):
    bl_idname = 'cameras.select'
    bl_label = 'Select Camera'
    bl_description = "Select camera"
    bl_options = {'REGISTER', 'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        if context.object.select_get():
            context.object.select_set(state=False)
        cam=bpy.data.objects[self.camera]
        cam.select_set(state=True)
        context.view_layer.objects.active = cam

        return{'FINISHED'}

#--------------------------------------------------------------------------------------
# P A N E L
#--------------------------------------------------------------------------------------

# CAMERAS LISTER
class CamerasLister(bpy.types.Operator):
    bl_label = "Cameras Lister"
    bl_idname = "cameras.lister"

    def draw(self, context):
        def coll_rec(coll, clist):
            if coll.children:
                for child in coll.children:
                    coll_rec(child, clist)
            cams=[cam.name for cam in coll.objects if cam.type=='CAMERA']
            if cams:
                cams.sort(key=str.lower)
                clist.append((coll.name, cams))
        
        layout = self.layout

        box = layout.column(align=True)
        box.label(text="CAMERAS", icon="OUTLINER_OB_CAMERA")
        box.separator()
        row = box.row(align=True)
        row.prop(context.scene, "sort_cameras", text=" ", expand=True)
        box.separator()
        boxframe = box.box()
        boxframecolumn = boxframe.column()
        sort_option = context.scene.sort_cameras
        if sort_option == sorting_cameras_options[0][0]:
            cam_list=[cam.name for cam in context.scene.collection.all_objects if cam.type=='CAMERA']
            cam_list.sort(key=str.lower)
            for cam in cam_list:
                row = boxframecolumn.row(align=True)
                row.operator("cameras.set_view", text=cam).camera=cam
                row.operator("cameras.select", text="", icon="RESTRICT_SELECT_OFF").camera=cam
        elif sort_option == sorting_cameras_options[1][0]:
            collcamlist=[]
            master_coll = context.scene.collection
            coll_rec(master_coll, collcamlist)
            collcamlist.sort()
            for coll in collcamlist:
                boxframecolumn.label(text=coll[0])
                for cam in coll[1]:
                    row = boxframecolumn.row(align=True)
                    row.operator("cameras.set_view", text=cam).camera=cam
                    row.operator("cameras.select", text="", icon="RESTRICT_SELECT_OFF").camera=cam

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_popup(self)

    def execute(self, context):
        self.report({'INFO'}, self.my_enum)
        return {'FINISHED'}

#--------------------------------------------------------------------------------------
# R E G I S T R Y
#--------------------------------------------------------------------------------------

classes = (
    SetCameraView,
    SelectCamera,
    CamerasLister
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    wm = bpy.context.window_manager

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
    kmi = km.keymap_items.new('cameras.lister', 'C', 'PRESS', alt=True)
    kmi.active = True

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)

    addon_keymaps = []
    
    wm = bpy.context.window_manager

    if wm.keyconfigs.addon:
        for km in addon_keymaps:
            for kmi in km.keymap_items:
                km.keymap_items.remove(kmi)

            wm.keyconfigs.addon.keymaps.remove(km)

    addon_keymaps.clear()

if __name__ == "__main__":
    register()