bl_info = {
    "name": "AutoSaver",
    "author": "Kaan Soyler",
    "version": (1, 0, 0),  
    "blender": (4, 2, 0),  
    "location": "View3D > Sidebar > AutoSaver",
    "description": "Automatically saves the Blender file at set intervals",
    "warning": "",
    "wiki_url": "",
    "category": "System",
}

import bpy
import time
from bpy.props import IntProperty, BoolProperty

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
                if bpy.data.is_saved:
                    bpy.ops.wm.save_mainfile()
                    self._last_save_time = current_time
                    self.report({'INFO'}, "File autosaved.")
                else:
                    self.report({'WARNING'}, "File has not been saved yet. Please save the file first.")
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

def unregister():
    bpy.utils.unregister_class(AutoSaverOperator)
    bpy.utils.unregister_class(AutoSaverStopOperator)
    bpy.utils.unregister_class(AutoSaverPanel)
    del bpy.types.Scene.auto_saver_interval
    del bpy.types.Scene.auto_saver_running

if __name__ == "__main__":
    register()
