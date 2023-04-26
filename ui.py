import bpy


def switch_packing_mode(image_packer, layout):
    if (image_packer.packing_mode == "square_packing"):
        row = layout.row()
        row.prop(image_packer, "img_size")
    elif (image_packer.packing_mode == "auto_sort"):
        row = layout.row()
    elif (image_packer.packing_mode == "row_packing"):
        pack_options = layout.column(align=True)
        pack_options.prop(image_packer, "side")
        pack_options.prop(image_packer, "side_mode")
        if (image_packer.side_mode == "custom"):
            pack_options.prop(image_packer, "side_length")

# == UI LISTS
class IMAGE_UL_PackingList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        custom_icon = 'IMAGE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)

# == PANELS
class IMAGE_PT_image_packer(bpy.types.Panel):
    bl_label = "Packed Image Options"
    bl_category = "Image Packer"
    bl_idname = "IMAGE_EDITOR_PT_image_packer_main"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        scene = context.scene
        image_packer = scene.image_packer
        layout = self.layout

        # Packed Image Options
        row = layout.row()
        row.prop(image_packer, "image_pack_name",icon_only=True)

        # Packing List
        box = layout.box()
        row = box.row()
        row.template_list("IMAGE_UL_PackingList", "Packing List", scene,
                          "image_packer_packing_list", scene, "image_packer_packing_list_index")

        row = row.column(align=True)
        row.operator("opr.image_packer_move_item", text="",
                     icon="TRIA_UP").direction = "UP"
        row.operator("opr.image_packer_move_item", text="",
                     icon="TRIA_DOWN").direction = "DOWN"

        # Packing List Options
        row = box.row()
        row.operator("opr.add_to_list", text="Add").list_name = "image_packer_packing_list"
        row.operator("opr.remove_from_list", text="Remove").list_name = "image_packer_packing_list"
        row.operator("opr.clear_list", text="Clear").list_name = "image_packer_packing_list"
        if scene.image_packer_packing_list_index >= 0 and scene.image_packer_packing_list:
            item = scene.image_packer_packing_list[scene.image_packer_packing_list_index]
            row = box.row()
            row.prop(item, "image")
        layout.separator(factor=0.5)

        # Packing Options
        box = layout.box()
        box.alignment = 'RIGHT'
        row = box.row(align=True)
        row.prop(image_packer, "packing_mode")
        switch_packing_mode(image_packer, box)
        if image_packer.packing_mode != "auto_sort": 
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(image_packer, "random_order")
            if image_packer.random_order:
                row.prop(image_packer, "random_seed", icon_only=True)

        # Generation Options
        row = box.row(align=True)
        row.prop(image_packer, "padding")
        row.prop(image_packer, "bg_color", icon_only=True)

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
        scene = context.scene
        image_packer = scene.image_packer
        layout = self.layout

        row = layout.row()
        row.prop(image_packer, "preview_window")

        box = layout.box()
        row = box.row()
        row.template_list("IMAGE_UL_PackingList", "Exlude List", scene,
                          "image_packer_exclude_list", scene, "image_packer_exclude_list_index")
        # Exclude List Options
        row = box.row()
        row.operator("opr.add_to_list", text="Add").list_name = "image_packer_exclude_list"
        row.operator("opr.remove_from_list", text="Remove").list_name = "image_packer_exclude_list"
        row.operator("opr.clear_list", text="Clear").list_name = "image_packer_exclude_list"

        row = layout.row()
        row.operator("opr.image_packer_remove_other_imgs",
                     text="Delete Other Images")
        row.separator(factor=1.5)

        # Test Shapes Options
        box = layout.box()
        box.label(text="Test Shapes Options")
        row = box.row()
        row.prop(image_packer, "amount", text="Shape Amount")
        row = box.row()
        row.prop(image_packer, "test_seed", text="Random Seed")

        row = box.row()
        row.prop(image_packer, "start_color", text="")
        row.prop(image_packer, "end_color", text="")

        col = box.column(align=True)
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

        row = box.row()
        row.operator("opr.image_packer_make_testshapes", text="Make Shapes")


classes = [
    IMAGE_UL_PackingList,
    IMAGE_PT_image_packer,
    IMAGE_PT_ExtraOptions,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
