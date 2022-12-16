import bpy


def switch_packing_mode(ImgCol, layout):
    if (ImgCol.packing_mode == "square_packing"):
        row = layout.row()
        row.prop(ImgCol, "img_size")
    elif (ImgCol.packing_mode == "auto_sort"):
        row = layout.row()
    elif (ImgCol.packing_mode == "row_packing"):
        pack_options = layout.column(align=True)
        pack_options.prop(ImgCol, "side")
        pack_options.prop(ImgCol, "side_mode")
        if (ImgCol.side_mode == "custom"):
            pack_options.prop(ImgCol, "side_length")

# == UI LISTS
class IMAGE_UL_ColImgs(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data,
                  active_propname, index):
        custom_icon = 'IMAGE'

        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name, icon=custom_icon)

        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text="", icon=custom_icon)

# == PANELS
class IMAGE_PT_ImgCol(bpy.types.Panel):
    bl_label = "Collection Options"
    bl_category = "Image Collection"
    bl_idname = "IMAGE_EDITOR_PT_ImgCol_main"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"

    def draw(self, context):
        scene = context.scene
        ImgCol = scene.ImgCol
        layout = self.layout

        # Collection Options
        row = layout.row()
        row.prop(ImgCol, "col_name",icon_only=True)

        # Collection Image List
        box = layout.box()
        row = box.row()
        row.template_list("IMAGE_UL_ColImgs", "Images in Collection", scene,
                          "col_list", scene, "col_list_index")

        row = row.column(align=True)
        row.operator("opr.imgcol_move_item", text="",
                     icon="TRIA_UP").direction = "UP"
        row.operator("opr.imgcol_move_item", text="",
                     icon="TRIA_DOWN").direction = "DOWN"

        # Image Options
        row = box.row()
        row.operator("opr.imgcol_add_image", text="Add")
        row.operator("opr.imgcol_remove_image", text="Remove")
        row.operator("opr.imgcol_clear", text="Clear")
        if scene.col_list_index >= 0 and scene.col_list:
            item = scene.col_list[scene.col_list_index]
            row = box.row()
            row.prop(item, "image")
        layout.separator(factor=0.5)

        box = layout.box()
        box.alignment = 'RIGHT'
        row = box.row(align=True)
        row.prop(ImgCol, "packing_mode")
        switch_packing_mode(ImgCol, box)
        if ImgCol.packing_mode != "auto_sort": 
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(ImgCol, "random_order")
            if ImgCol.random_order:
                row.prop(ImgCol, "random_seed", icon_only=True)

        # Generation Options
        row = box.row(align=True)
        row.prop(ImgCol, "padding")
        row.prop(ImgCol, "bg_color", icon_only=True)

        col = layout.column(align=True)
        row = col.row()
        row.scale_y = 1.5
        row.operator("opr.imgcol_generate", icon="PLAY",
                     text="Make Collection")
        row = col.row(align=True)
        row.operator("opr.imgcol_preview", text="Preview")
        row.operator("opr.imgcol_remove", text="Remove")


class IMAGE_PT_ExtraOptions(bpy.types.Panel):
    bl_label = "Extra Options"
    bl_category = "Image Collection"
    bl_idname = "IMAGE_EDITOR_PT_ImgCol_extra"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        ImgCol = context.scene.ImgCol
        layout = self.layout

        row = layout.row()
        row.operator("opr.imgcol_remove_other_imgs",
                     text="Delete Other Images")
        row.separator(factor=1.5)

        # Test Shapes Options
        box = layout.box()
        box.label(text="Test Shapes Options")
        row = box.row()
        row.prop(ImgCol, "amount", text="Shape Amount")
        row = box.row()
        row.prop(ImgCol, "test_seed", text="Random Seed")

        row = box.row()
        row.prop(ImgCol, "start_color", text="")
        row.prop(ImgCol, "end_color", text="")

        col = box.column(align=True)
        row = col.row(align=True)
        row.separator()
        r = row.split(factor=0.2, align=True)
        r.alignment = 'CENTER'
        r.label(text="Width")
        r.alignment = 'EXPAND'
        r.prop(ImgCol, "min_width", icon_only=True)
        r.prop(ImgCol, "max_width", icon_only=True)

        col.separator()

        row = col.row(align=True)
        row.separator()
        r = row.split(factor=0.2, align=True)
        r.alignment = 'CENTER'
        r.label(text="Height")
        r.alignment = 'EXPAND'
        r.prop(ImgCol, "min_height", icon_only=True)
        r.prop(ImgCol, "max_height", icon_only=True)

        row = box.row()
        row.operator("opr.imgcol_make_testshapes", text="Make Shapes")


classes = [
    IMAGE_UL_ColImgs,
    IMAGE_PT_ImgCol,
    IMAGE_PT_ExtraOptions,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
