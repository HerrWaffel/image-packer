import bpy


def switch_packing_mode(image_packer, layout):
    if (image_packer.packing_mode == "square_packing"):
        row = layout.row()
        row.prop(image_packer, "img_size")
    elif (image_packer.packing_mode == "row_packing" or image_packer.packing_mode == "col_packing"):
        pack_options = layout.column(align=True)
        pack_options.prop(image_packer, "side_mode")
        if image_packer.side_mode == "custom":
            if image_packer.packing_mode == "row_packing":
                pack_options.prop(image_packer, "side_length", text="Height")
            else:
                pack_options.prop(image_packer, "side_length", text="Width")

# == IMAGE LISTS
class IMAGE_UL_PackingList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        custom_icon = 'IMAGE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)


# == MAIN PANEL
class IMAGE_PT_image_packer(bpy.types.Panel):
    bl_label = "Image Packer"
    bl_category = "Image Packer"
    bl_idname = "IMAGE_EDITOR_PT_image_packer_main"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        return

# == MAIN SUBPANELS
class IMAGE_PT_PackingList(bpy.types.Panel):
    bl_label = "Packing List"
    bl_category = "Image Packer"
    bl_idname = "IMAGE_EDITOR_PT_packing_list"
    bl_parent_id = "IMAGE_EDITOR_PT_image_packer_main"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        scene = context.scene
        layout = self.layout

        # Packing List
        layout.label(text="Packing List")
        list_row = layout.row()
        col = list_row.column()
        col.template_list("IMAGE_UL_PackingList", "Packing List", scene,
                          "image_packer_packing_list", scene, "image_packer_packing_list_index")
        
        # Packing Item Options
        if scene.image_packer_packing_list_index >= 0 and scene.image_packer_packing_list:
            item = scene.image_packer_packing_list[scene.image_packer_packing_list_index]
            col.prop(item, "image", text="")

        # Packing List Operators
        col.separator(factor=0.5)
        row = col.row(align=True)
        row.operator("opr.add_to_packing_list", text="Add")
        row.operator("opr.remove_from_packing_list", text="Remove")
        row.operator("opr.clear_packing_list", text="Clear")
        
        # Move List Operators
        move_col = list_row.column(align=True)
        move_col.operator("opr.image_packer_move_item", text="",
                     icon="TRIA_UP").direction = "UP"
        move_col.operator("opr.image_packer_move_item", text="",
                     icon="TRIA_DOWN").direction = "DOWN"   

class IMAGE_PT_PackingOptions(bpy.types.Panel):
    bl_label = "Packing Options"
    bl_category = "Image Packer"
    bl_idname = "IMAGE_EDITOR_PT_packing_options"
    bl_parent_id = "IMAGE_EDITOR_PT_image_packer_main"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        scene = context.scene
        image_packer = scene.image_packer
        layout = self.layout

        row = layout.row(align=True)
        row.prop(image_packer, "packing_mode", text="")

        switch_packing_mode(image_packer, layout)

        col = layout.column(align=True)
        row = col.row(align=True)
        row.prop(image_packer, "random_order")
        if image_packer.random_order:
            row.prop(image_packer, "random_seed", icon_only=True)  

        # Generation Options
        row = layout.row(align=True)
        row.prop(image_packer, "padding")
        row.prop(image_packer, "bg_color", icon_only=True)

class IMAGE_PT_PackingOpr(bpy.types.Panel):
    bl_label = "Packing Operators"
    bl_category = "Image Packer"
    bl_idname = "IMAGE_EDITOR_PT_packing_opr"
    bl_parent_id = "IMAGE_EDITOR_PT_image_packer_main"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_options = {'HIDE_HEADER'}

    def draw(self, context):
        layout = self.layout
        # layout.use_property_decorate = False
        image_packer = context.scene.image_packer

        # Packed Image Name
        row = layout.row()
        row.prop(image_packer, "image_pack_name", icon_only=True)

        col = layout.column(align=True)
        row = col.row()
        row.scale_y = 1.5
        row.operator("opr.image_packer_generate", icon="PLAY",
                     text="Pack Images")
        row = col.row(align=True)
        row.operator("opr.image_packer_preview", text="Preview")
        row.operator("opr.image_packer_remove", text="Remove")


class IMAGE_PT_ExtraOptions(bpy.types.Panel):
    bl_label = "Extra Options"
    bl_category = "Image Packer"
    bl_idname = "IMAGE_EDITOR_PT_image_packer_extra"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        self.layout.operator("opr.image_packer_remove_other_imgs",
                     text="Delete Unused Images")
        self.layout.operator("opr.image_packer_add_all_imgs",
                             text="Add All Images")

# == EXTRA SUBPANELS       
class IMAGE_PT_TestShapes(bpy.types.Panel):
    bl_label = "Test Shapes"
    bl_category = "Extra Options"
    bl_idname = "IMAGE_EDITOR_PT_test_shapes"
    bl_parent_id = "IMAGE_EDITOR_PT_image_packer_extra"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        scene = context.scene
        image_packer = scene.image_packer
        layout = self.layout

        row = layout.row()
        row.prop(image_packer, "amount", text="Shape Amount")
        row = layout.row()
        row.prop(image_packer, "test_seed", text="Random Seed")

        row = layout.row(align=True)
        row.prop(image_packer, "start_color", text="")
        row.prop(image_packer, "end_color", text="")

        col = layout.column(align=True)
        row = col.row(align=True)
        row.separator()
        r = row.split(factor=0.2, align=True)
        r.alignment = 'CENTER'
        r.label(text="Width")
        r.alignment = 'EXPAND'
        r.prop(image_packer, "min_width", icon_only=True)
        r.prop(image_packer, "max_width", icon_only=True)

        col.separator()

        row = col.row(align=True)
        row.separator()
        r = row.split(factor=0.2, align=True)
        r.alignment = 'CENTER'
        r.label(text="Height")
        r.alignment = 'EXPAND'
        r.prop(image_packer, "min_height", icon_only=True)
        r.prop(image_packer, "max_height", icon_only=True)

        row = layout.row()
        row.operator("opr.image_packer_make_testshapes", text="Make Shapes")


classes = [
    IMAGE_UL_PackingList,
    IMAGE_PT_image_packer,
    IMAGE_PT_PackingList,
    IMAGE_PT_PackingOptions,
    IMAGE_PT_ExtraOptions,
    IMAGE_PT_TestShapes,
    IMAGE_PT_PackingOpr,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
