import bpy
from bpy.props import (
    IntProperty,
    EnumProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
    CollectionProperty,
    FloatVectorProperty,
)

class ImagePackerPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    preview_window: BoolProperty(
        name="Seperate Preview Window",
        default=False,
        description="Preview the packed image in a seperate window"
    )

    auto_open_preview: BoolProperty(
        name="Preview on Pack",
        default=True,
        description="Preview the packed image once all images are packed"
    )

    allow_duplicates: BoolProperty(
        name="Allow Duplicates",
        default=False,
        description="Allow adding duplicate images to the packing list"
    )
    
    exclude_existing_imgs: BoolProperty(
        name="Always Add Existing Images to Exclude List",
        default=True,
        description="Adds all existing images to the exclude list. This prevents the option 'Remove All Images' from deleting existing images"
    )

    def draw(self, context):
        layout = self.layout

        # Display the preferences properties in the preferences panel
        box = layout.box()
        box.label(text="Preview Settings")
        box.prop(self, "preview_window")
        box.prop(self, "auto_open_preview")

        box = layout.box()
        box.label(text="Packing List Settings")
        box.prop(self, "allow_duplicates")

        # Add a button to apply the preferences
        layout.operator("opr.image_packer_apply_preferences")

class ApplyPreferencesOpr(bpy.types.Operator):
    bl_idname = "opr.image_packer_apply_preferences"
    bl_label = "Apply Preferences"

    def execute(self, context):
        # Access the preferences and apply them here
        preferences = context.preferences.addons[__package__].preferences

        # Apply the preferences to your addon logic
        # ...

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ImagePackerPreferences)
    bpy.utils.register_class(ApplyPreferencesOpr)

def unregister():
    bpy.utils.unregister_class(ImagePackerPreferences)
    bpy.utils.unregister_class(ApplyPreferencesOpr)

if __name__ == "__main__":
    register()
