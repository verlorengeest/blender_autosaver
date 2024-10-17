bl_info = {
    "name": "AutoSaver",
    "author": "Kaan Soyler",
    "version": (1, 1, 0),  
    "blender": (4, 2, 0),  
    "location": "View3D > Sidebar > AutoSaver",
    "description": "Automatically saves the Blender file at set intervals",
    "warning": "",
    "wiki_url": "",
    "category": "System",
}

import bpy
import time
import os
import uuid
from bpy.props import IntProperty, BoolProperty, StringProperty

class AutoSaverOperator(bpy.types.Operator):
    """Operator that autosaves the file at set intervals"""
    bl_idname = "wm.auto_saver_operator"
    bl_label = "Start AutoSaver"

    _timer = None
    _last_save_time = 0

    def modal(self, context, event):
        if not context.scene.auto_saver_running:
            self.cancel(context)
            return {'CANCELLED'}

        if event.type == 'TIMER':
            current_time = time.time()
            interval = context.scene.auto_saver_interval

            if current_time - self._last_save_time >= interval:
                directory = context.scene.auto_saver_directory
                unique_names = context.scene.auto_saver_unique_names

                if bpy.data.is_saved:
                    if unique_names:
                        # Save as a new file each time
                        file_path = bpy.data.filepath
                        dir_name = os.path.dirname(file_path)
                        base_name = os.path.basename(file_path)
                        name, ext = os.path.splitext(base_name)
                        timestamp = time.strftime("%Y%m%d_%H%M%S")
                        new_name = f"{name}_{timestamp}{ext}"
                        new_path = os.path.join(dir_name, new_name)
                        bpy.ops.wm.save_as_mainfile(filepath=new_path, copy=True)
                    else:
                        # Overwrite the current file
                        bpy.ops.wm.save_mainfile()
                    self._last_save_time = current_time
                    self.report({'INFO'}, "File autosaved.")
                else:
                    # File has not been saved yet
                    if directory:
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        random_name = f"autosave_{uuid.uuid4().hex[:8]}.blend"
                        save_path = os.path.join(directory, random_name)
                        bpy.ops.wm.save_as_mainfile(filepath=save_path, copy=False)
                        self._last_save_time = current_time
                        self.report({'INFO'}, f"File autosaved as {random_name}.")
                    else:
                        self.report({'WARNING'}, "Autosave directory not set. Please set it in the AutoSaver panel.")
            return {'PASS_THROUGH'}

        return {'PASS_THROUGH'}

    def execute(self, context):
        if context.scene.auto_saver_running:
            self.report({'WARNING'}, "AutoSaver is already running.")
            return {'CANCELLED'}

        context.scene.auto_saver_running = True
        wm = context.window_manager
        self._timer = wm.event_timer_add(1.0, window=context.window)
        self._last_save_time = time.time()
        wm.modal_handler_add(self)
        self.report({'INFO'}, "AutoSaver started.")
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager
        wm.event_timer_remove(self._timer)
        context.scene.auto_saver_running = False
        self.report({'INFO'}, "AutoSaver stopped.")

class AutoSaverStopOperator(bpy.types.Operator):
    """Stop the AutoSaver Operator"""
    bl_idname = "wm.auto_saver_stop"
    bl_label = "Stop AutoSaver"

    def execute(self, context):
        context.scene.auto_saver_running = False
        self.report({'INFO'}, "AutoSaver stopped.")
        return {'FINISHED'}

class AutoSaverPanel(bpy.types.Panel):
    """Creates a Panel in the View3D Sidebar"""
    bl_label = "AutoSaver"
    bl_idname = "VIEW3D_PT_auto_saver"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "AutoSaver"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.prop(scene, "auto_saver_interval")
        layout.prop(scene, "auto_saver_directory")
        layout.prop(scene, "auto_saver_unique_names")
        row = layout.row()
        if not scene.auto_saver_running:
            row.operator("wm.auto_saver_operator", text="Start AutoSaver")
        else:
            row.operator("wm.auto_saver_stop", text="Stop AutoSaver")

def register():
    bpy.utils.register_class(AutoSaverOperator)
    bpy.utils.register_class(AutoSaverStopOperator)
    bpy.utils.register_class(AutoSaverPanel)
    bpy.types.Scene.auto_saver_interval = IntProperty(
        name="Interval (seconds)",
        description="Time interval between autosaves",
        default=300,
        min=10,
    )
    bpy.types.Scene.auto_saver_running = BoolProperty(
        name="AutoSaver Running",
        description="Indicates if AutoSaver is running",
        default=False,
    )
    bpy.types.Scene.auto_saver_directory = StringProperty(
        name="Autosave Directory",
        description="Directory where to save autosaves if the file hasn't been saved yet",
        subtype='DIR_PATH',
        default=""
    )
    bpy.types.Scene.auto_saver_unique_names = BoolProperty(
        name="Save as Different Files",
        description="Save as different files each time",
        default=False
    )

def unregister():
    bpy.utils.unregister_class(AutoSaverOperator)
    bpy.utils.unregister_class(AutoSaverStopOperator)
    bpy.utils.unregister_class(AutoSaverPanel)
    del bpy.types.Scene.auto_saver_interval
    del bpy.types.Scene.auto_saver_running
    del bpy.types.Scene.auto_saver_directory
    del bpy.types.Scene.auto_saver_unique_names

if __name__ == "__main__":
    register()
