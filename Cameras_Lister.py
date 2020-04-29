bl_info = {
    "name": "Cameras Lister",
    "blender": (2, 82, 0),
    "description": "Lists all cameras from the scene and allows to easily set the view to a particular one.",
    "location": "Camera Lister's panel shortcut: Alt + C",
    "category": "Camera"
}

import bpy
from bpy.types import Operator, Menu, Panel, PropertyGroup, PointerProperty, Object

#--------------------------------------------------------------------------------------
# F E A T U R E S
#--------------------------------------------------------------------------------------

# CAMERA'S CUSTOM RESOLUTION
class Camera_Custom_Resolution_Settings(PropertyGroup):
    Custom_Horizontal_Resolution: bpy.props.IntProperty(
        name="Custom Horizontal Resolution",
        description="Custom Horizontal Resolution",
        default = 1920)
        
    Custom_Vertical_Resolution: bpy.props.IntProperty(
        name="Custom Vertical Resolution",
        description="Custom Vertical Resolution",
        default = 1080)

# SET CAMERA CUSTOM RESOLUTION
def SetCameraCustomResolution(self, context):
    context.scene.render.resolution_x = context.active_object.camera_custom_resolution_settings_pointer_prop.Custom_Horizontal_Resolution
    context.scene.render.resolution_y = context.active_object.camera_custom_resolution_settings_pointer_prop.Custom_Vertical_Resolution

# CAMERA VIEW OFF
class CameraViewOff(bpy.types.Operator):
    bl_idname = 'cameras.camera_view_off'
    bl_label = 'Camera View Off'
    bl_description = "Camera View Off"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()
    
    def execute(self,context):
        context.area.spaces[0].region_3d.view_perspective='PERSP'

        return{'FINISHED'}

# ALIGN SELECTED CAMERA TO VIEW
class AlignSelectedCameraToView(bpy.types.Operator):
    bl_idname = 'cameras.align_selected_to_view'
    bl_label = 'Align Selected to View'
    bl_description = "Align selected camera to view"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.object:
            if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
                return {'FINISHED'}
            else:
                ob = context.object
                if ob.type == 'CAMERA':
                    scene = bpy.context.scene
                    currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
                    scene.camera = currentCameraObj
                    bpy.ops.view3d.camera_to_view()

        return{'FINISHED'}

# NEW CAMERA FROM VIEW
class NewCameraFromView(bpy.types.Operator):
    bl_idname = 'cameras.new_from_view'
    bl_label = 'New Camera From View'
    bl_description = "Create a new camera from view"
    bl_options = {'UNDO'}

    def execute(self,context):
        if context.area.spaces[0].region_3d.view_perspective == 'CAMERA':
            context.area.spaces[0].region_3d.view_perspective='PERSP'
        bpy.ops.object.camera_add()
        scene = bpy.context.scene
        currentCameraObj = bpy.data.objects[bpy.context.active_object.name]
        scene.camera = currentCameraObj
        bpy.ops.view3d.camera_to_view()

        return{'FINISHED'}

# RENDER ENGINE OPTIONS
def update_render_engine(self, context):
    selected_engine = context.scene.set_render_engine
    
    if selected_engine == render_engine_options[0][0]:
        bpy.context.scene.render.engine = 'BLENDER_EEVEE'
    if selected_engine == render_engine_options[1][0]:
        bpy.context.scene.render.engine = 'CYCLES'

render_engine_options = [
        ("eevee", "EEVEE", ""),
        ("cycles", "CYCLES", "")]

bpy.types.Scene.set_render_engine = bpy.props.EnumProperty(
    items=render_engine_options,
    description="Set render engine",
    default= "eevee",
    update = update_render_engine)

# SORTING CAMERAS OPTIONS
sorting_cameras_options = [
        ("alphabetically", "Alphabetically", ""),
        ("by_collections", "By Collections", "")]

bpy.types.Scene.sort_cameras = bpy.props.EnumProperty(
    items=sorting_cameras_options,
    description="Sort cameras",
    default= "alphabetically")

# SET CAMERA VIEW
class SetCameraView(bpy.types.Operator):
    bl_idname = 'cameras.set_view'
    bl_label = 'Set Camera View'
    bl_description = "Set View to this Camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        if bpy.context.object.hide_get(view_layer=None):
            bpy.context.object.hide_set(False)
            bpy.ops.cameras.select(camera=self.camera)
            bpy.ops.view3d.object_as_camera()
            bpy.ops.view3d.view_center_camera()
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
        else:
            bpy.ops.cameras.select(camera=self.camera)
            bpy.ops.view3d.object_as_camera()
            bpy.ops.view3d.view_center_camera()
            SetCameraCustomResolution(self, context)

        return{'FINISHED'}

# SELECT CAMERA
class SelectCamera(bpy.types.Operator):
    bl_idname = 'cameras.select'
    bl_label = 'Select Camera'
    bl_description = "Select camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        if context.object:
            if context.object.select_get():
                context.object.select_set(state=False)
        cam=bpy.data.objects[self.camera]
        cam.select_set(state=True)
        context.view_layer.objects.active = cam
        context.scene.camera=cam
        
        if bpy.context.object.hide_get(view_layer=None):
            bpy.context.object.hide_set(False)
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
        else:
            SetCameraCustomResolution(self, context)
        
        return{'FINISHED'}

# BIND CAMERA TO MARKER
class BindCameraToMarker(bpy.types.Operator):
    bl_idname = 'cameras.bind_to_marker'
    bl_label = 'Bind Camera to Marker'
    bl_description = "Bind camera to marker at current frame"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
                
        tm = bpy.context.scene.timeline_markers
        cur_frame = context.scene.frame_current
        frame_markers = [marker for marker in tm if marker.frame == cur_frame]

        if len(frame_markers) == 0:
            new_marker = tm.new(self.camera, frame = cur_frame)
            new_marker.camera = bpy.data.objects[self.camera]
        elif len(frame_markers) >= 1:
            for marker in frame_markers:
                tm.remove(marker)
            new_marker = tm.new(self.camera, frame = cur_frame)
            new_marker.camera = bpy.data.objects[self.camera]
        
        return{'FINISHED'}

# DELETE CAMERA MARKER
class Delete_Camera_Marker(bpy.types.Operator):
    bl_idname = 'cameras.delete_camera_marker'
    bl_label = 'Delete Camera Marker'
    bl_description = "Delete camera marker at current frame"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        
        tm = bpy.context.scene.timeline_markers
        cur_frame = context.scene.frame_current
        frame_markers = [marker for marker in tm if marker.frame == cur_frame]
        
        for marker in frame_markers:
            if marker.name == self.camera:
                tm.remove(frame_markers[0])

        return{'FINISHED'}

# DELETE CAMERA
class DeleteCamera(bpy.types.Operator):
    bl_idname = 'cameras.delete'
    bl_label = 'Delete Camera'
    bl_description = "Delete camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        cam=bpy.data.objects[self.camera]
        bpy.data.objects.remove(cam)
        
        tm = bpy.context.scene.timeline_markers
        for marker in tm:
            if marker.name == self.camera:
                 tm.remove(marker)
        
        return{'FINISHED'}

# PANEL BUTTON - CAMERA SETTINGS
class PanelButton_CameraSettings(bpy.types.Operator):
    bl_idname = "camera.settings"
    bl_label = "Camera Settings"
    bl_description = "Select camera"
    bl_options = {'UNDO'}

    camera: bpy.props.StringProperty()

    def execute(self,context):
        pass

    def draw(self, context):
        layout = self.layout

        cam = bpy.context.object.data
        layout.label(text="RENDER SETTINGS", icon="RESTRICT_RENDER_OFF")
        col = layout.column(align=False)
        row = col.row()
        row.prop(cam, "type", text="")
        
        if cam.type == 'PERSP':
            row = col.row()
            row.prop(cam, "lens_unit", text="")
            if cam.lens_unit == 'MILLIMETERS':
                row.prop(cam, "lens", text="Focal")
            elif cam.lens_unit == 'FOV':
                row.prop(cam, "angle", text="Field of View")
            
        elif cam.type == 'ORTHO':
            row.prop(cam, "ortho_scale", text="Scale")
            
        elif cam.type == 'PANO':
            engine = context.engine
            if engine == 'CYCLES':
                ccam = cam.cycles
                row.prop(ccam, "panorama_type", text="")
                
                if ccam.panorama_type == 'FISHEYE_EQUIDISTANT':
                    row = col.row()
                    row.prop(ccam, "fisheye_fov", text="Field of View")
                    
                elif ccam.panorama_type == 'FISHEYE_EQUISOLID':
                    row = col.row()
                    row.prop(ccam, "fisheye_lens", text="Lens")
                    row.prop(ccam, "fisheye_fov", text="FOV")
                    
                elif ccam.panorama_type == 'EQUIRECTANGULAR':
                    row = col.row()
                    row.prop(ccam, "latitude_min", text="Latitude Min")
                    row.prop(ccam, "longitude_min", text="Longitude Min")
                    row = col.row()                            
                    row.prop(ccam, "latitude_max", text="Latitude Max")
                    row.prop(ccam, "longitude_max", text="Longitude Max")
        
        row = col.row()
        row.label(text="Shift:")
        row.label(text="Clip:")
        row = col.row()
        row.prop(cam, "shift_x", text="Horizontal")
        row.prop(cam, "clip_start", text="Start")
        row = col.row()
        row.prop(cam, "shift_y", text="Vertical")
        row.prop(cam, "clip_end", text="End")
        layout.label(text="Custom Resolution:")
        row = layout.row(align=False)
        if bpy.context.object.hide_get(view_layer=None):
            rowbox = row.box()
            rowbox.alert =True
            rowbox.label(text="Unhide Camera in viewport to setup resolution", icon= "ERROR")
        else:
            row.prop(context.active_object.camera_custom_resolution_settings_pointer_prop, "Custom_Horizontal_Resolution", text="Horizontal")
            row.prop(context.active_object.camera_custom_resolution_settings_pointer_prop, "Custom_Vertical_Resolution", text="Vertical")
        
    def invoke(self, context, event):
        
        if context.object:
            if context.object.select_get():
                context.object.select_set(state=False)
        cam=bpy.data.objects[self.camera]
        cam.select_set(state=True)
        context.view_layer.objects.active = cam
        context.scene.camera=cam

        if bpy.context.object.hide_get(view_layer=None):
            bpy.context.object.hide_set(False)
            SetCameraCustomResolution(self, context)
            bpy.context.object.hide_set(True)
        else:
            SetCameraCustomResolution(self, context)

        wm = context.window_manager
        return wm.invoke_popup(self)

#--------------------------------------------------------------------------------------
# C A M E R A S   L I S T E R   P A N E L
#--------------------------------------------------------------------------------------

# CAMERAS LISTER PANEL
def common_draw(self,layout,context):
    def coll_rec(coll, clist):
        if coll.children:
            for child in coll.children:
                coll_rec(child, clist)
        cams=[cam.name for cam in coll.objects if cam.type=='CAMERA']
        if cams:
            cams.sort(key=str.lower)
            clist.append((coll.name, cams))

    tm = bpy.context.scene.timeline_markers
    cur_frame = context.scene.frame_current
    frame_markers = [marker for marker in tm if marker.frame == cur_frame]

    box = layout
    row = box.row(align=False)
    row.scale_x = 1.8
    row.scale_y = 1.8
    row.operator("render.render", text="", icon="RENDER_STILL")
    row.operator("render.render", text="", icon="RENDER_ANIMATION").animation=True
    row.operator("render.view_show", text="", icon="IMAGE_DATA")
    if ((context.area.spaces[0].region_3d.view_perspective == 'PERSP' or context.area.spaces[0].region_3d.view_perspective == 'ORTHO')
    and context.area.spaces.active.use_render_border == False):
        row.operator("view3d.render_border", text="", icon="BORDERMOVE")
    elif ((context.area.spaces[0].region_3d.view_perspective == 'PERSP' or context.area.spaces[0].region_3d.view_perspective == 'ORTHO')
    and context.area.spaces.active.use_render_border == True):
        row.alert = True
        row.operator("view3d.clear_render_border", text="", icon="BORDERMOVE")
    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' and bpy.data.scenes["Scene"].render.use_border == False:
        row.operator("view3d.render_border", text="", icon="BORDERMOVE")
    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA' and bpy.data.scenes["Scene"].render.use_border == True:
        row.alert = True
        row.operator("view3d.clear_render_border", text="", icon="BORDERMOVE")
    row.prop(context.scene, "set_render_engine", text=" ", expand=True)
    box.separator()
    row = box.row(align=False)
    row.scale_y = 1.2
    row.operator("cameras.new_from_view", text="Add Camera to View", icon="ADD")
    row.operator("cameras.align_selected_to_view", text="Align Selected to View", icon="CON_CAMERASOLVER")
    box.separator()
    boxframe = box.box()
    row = boxframe.row(align=True)
    row.prop(context.scene, "sort_cameras", text=" ", expand=True)
    boxframe = box.box()
    boxframecolumn = boxframe.column()
    sort_option = context.scene.sort_cameras
    if sort_option == sorting_cameras_options[0][0]:
        cam_list=[cam.name for cam in context.scene.collection.all_objects if cam.type=='CAMERA']
        cam_list.sort(key=str.lower)
        if not cam_list:
            row = boxframecolumn.row(align=True)
            row.alignment = "CENTER"
            row.alert = True
            row.label(text="No cameras in this scene", icon= "ERROR")
        else:
            for cam in cam_list:
                row = boxframecolumn.row(align=True)
                row.operator("cameras.select", text="", icon="RESTRICT_SELECT_OFF").camera=cam
                row.operator("cameras.camera_view_off"
                    if context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
                    and bpy.context.space_data.camera is bpy.context.scene.objects[cam] else "cameras.set_view",
                    text=cam, icon="CHECKBOX_HLT"
                    if bpy.context.space_data.camera is bpy.context.scene.objects[cam]
                    and context.object.type == 'CAMERA'
                    and context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
                    else "CHECKBOX_DEHLT").camera=cam
                row.operator("cameras.delete_camera_marker"
                    if len(frame_markers) >= 1 and frame_markers[0].name == cam else "cameras.bind_to_marker",
                    text="", icon="MARKER_HLT" if len(frame_markers) >= 1 and frame_markers[0].name == cam else "MARKER").camera=cam
                row.operator("cameras.delete", text="", icon="PANEL_CLOSE").camera=cam
                row.separator()
                row.operator("camera.settings", text="", icon="TRIA_RIGHT").camera=cam
                
    elif sort_option == sorting_cameras_options[1][0]:
        collcamlist=[]
        master_coll = context.scene.collection
        coll_rec(master_coll, collcamlist)
        collcamlist.sort()
        if not collcamlist:
            row = boxframecolumn.row(align=True)
            row.alignment = "CENTER"
            row.alert = True
            row.label(text="No cameras in this scene", icon= "ERROR")
        else:
            for coll in collcamlist:
                boxframecolumn.label(text=coll[0])
                for cam in coll[1]:
                    row = boxframecolumn.row(align=True)
                    row.operator("cameras.select", text="", icon="RESTRICT_SELECT_OFF").camera=cam
                    row.operator("cameras.camera_view_off"
                        if context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
                        and bpy.context.space_data.camera is bpy.context.scene.objects[cam] else "cameras.set_view",
                        text=cam, icon="CHECKBOX_HLT"
                        if bpy.context.space_data.camera is bpy.context.scene.objects[cam]
                        and context.object.type == 'CAMERA'
                        and context.area.spaces[0].region_3d.view_perspective == 'CAMERA'
                        else "CHECKBOX_DEHLT").camera=cam
                    row.operator("cameras.delete_camera_marker"
                        if len(frame_markers) >= 1 and frame_markers[0].name == cam else "cameras.bind_to_marker",
                        text="", icon="MARKER_HLT" if len(frame_markers) >= 1 and frame_markers[0].name == cam else "MARKER").camera=cam
                    row.operator("cameras.delete", text="", icon="PANEL_CLOSE").camera=cam
                    row.separator()
                    row.operator("camera.settings", text="", icon="TRIA_RIGHT").camera=cam

#--------------------------------------------------------------------------------------
# P A N E L
#--------------------------------------------------------------------------------------

# FLOATING PANEL
class VIEW3D_PT_FloatingPanel(Operator):
    bl_label = "Cameras Lister"
    bl_idname = "cameras.lister"

    def draw(self, context):
        layout = self.layout
        box = layout.column(align=True)
        box.label(text="CAMERAS LISTER", icon="OUTLINER_OB_CAMERA")
        box.separator()
        common_draw(self, box, context)
        
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
    Camera_Custom_Resolution_Settings,
    CameraViewOff,
    AlignSelectedCameraToView,
    NewCameraFromView,
    SetCameraView,
    SelectCamera,
    BindCameraToMarker,
    Delete_Camera_Marker,
    DeleteCamera,
    PanelButton_CameraSettings,
    VIEW3D_PT_FloatingPanel,
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    Object.camera_custom_resolution_settings_pointer_prop = bpy.props.PointerProperty(type = Camera_Custom_Resolution_Settings)

    wm = bpy.context.window_manager

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name = 'Object Mode')
    kmi = km.keymap_items.new('cameras.lister', 'C', 'PRESS', alt=True)
    kmi.active = True

def unregister():
    from bpy.utils import unregister_class
    for cls in classes:
        unregister_class(cls)
    
    del Object.Pointer_Camera_Custom_Resolution_Settings

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