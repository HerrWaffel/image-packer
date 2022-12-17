import bpy
from bpy.types import Operator
from .utils import (
    GetActiveImage, 
    RandomizeImageOrder, 
    PreviewColImage, 
    CreateTestImgs,
    DeleteImage,
)
from .packing_modes import (
    SquarePacking,
    AutoSort,
    RowPacking,
    NextFitPacking,
)


class GenerateOpr(Operator):
    bl_label = "Generate Collection"
    bl_idname = "opr.imgcol_generate"

    @classmethod
    def poll(cls, context):
        return context.scene.col_list
        
    def execute(self, context):
        scene = context.scene
        ImgCol = scene.ImgCol

        img_list = []
        for img in context.scene.col_list:
            img_list.append(img["image"])

        if ImgCol.random_order:
            RandomizeImageOrder(img_list)

        match ImgCol.packing_mode:
            case "square_packing":
                SquarePacking(img_list, ImgCol)
            case "auto_sort":
                AutoSort(img_list, ImgCol)
            case "row_packing":
                RowPacking(img_list, ImgCol)
            case "nextfit_packing":
                NextFitPacking(img_list, ImgCol)
        if GetActiveImage() == None:
            col_img = bpy.data.images.get(ImgCol.col_name)
            bpy.context.area.spaces.active.image = col_img
        return {"FINISHED"}


class PreviewOpr(Operator):
    bl_label = "Preview Collection"
    bl_idname = "opr.imgcol_preview"

    def execute(self, context):
        PreviewColImage(bpy.data.images.get(
            bpy.context.scene.ImgCol.col_name))
        return {"FINISHED"}


class RemoveColOpr(Operator):
    bl_label = "remove Collection"
    bl_idname = "opr.imgcol_remove"

    def execute(self, context):
        try:
            DeleteImage(bpy.data.images.get(
                bpy.context.scene.ImgCol.col_name))
        except:
            print("No collection found with the name: {}".format(bpy.context.scene.ImgCol.col_name))
        return {"FINISHED"}


class AddImageOpr(Operator):
    bl_label = "Add Image To Collection"
    bl_idname = "opr.imgcol_add_image"

    def execute(self, context):
        col_list = context.scene.col_list
        new_image = GetActiveImage()

        name_list = []
        for item in col_list:
            name_list.append(item.name)

        if new_image.name not in name_list:
            col_list.add()
            col_list[-1].image = new_image
            col_list[-1].name = new_image.name

        return {"FINISHED"}


class RemoveImageOpr(Operator):
    bl_label = "Removes selected image from collection"
    bl_idname = "opr.imgcol_remove_image"

    @classmethod
    def poll(cls, context):
        return context.scene.col_list

    def execute(self, context):
        col_list = context.scene.col_list
        index = context.scene.col_list_index

        col_list.remove(index)
        context.scene.col_list_index = min(
            max(0, index - 1), len(col_list) - 1)

        return {'FINISHED'}


class ClearColOpr(Operator):
    bl_label = "Clears all images in the collection"
    bl_idname = "opr.imgcol_clear"

    @classmethod
    def poll(cls, context):
        return context.scene.col_list

    def execute(self, context):
        context.scene.col_list.clear()
        context.scene.col_list_index = 0
        return {'FINISHED'}


class MoveItemOpr(Operator):
    bl_label = "Move an item in the collection"
    bl_idname = "opr.imgcol_move_item"

    direction: bpy.props.EnumProperty(
        items=(('UP', 'Up', ""),
               ('DOWN', 'Down', ""),
               ))

    @classmethod
    def poll(cls, context):
        return context.scene.col_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.col_list_index
        list_length = len(bpy.context.scene.col_list) - \
            1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.col_list_index = max(0, min(new_index, list_length))

    def execute(self, context):
        col_list = context.scene.col_list
        index = context.scene.col_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        col_list.move(neighbor, index)
        self.move_index()

        return {'FINISHED'}


class RemoveOtherImgOpr(Operator):
    bl_label = "remove Other Images not in the collection list"
    bl_idname = "opr.imgcol_remove_other_imgs"

    def execute(self, context):
        scene = context.scene

        col_list = scene.col_list
        name_list = []
        for item in col_list:
            name_list.append(item.name)

        all_images = bpy.data.images
        for image in all_images:
            if not (image.name in name_list or image.name == scene.ImgCol.col_name):
                all_images.remove(image)

        return {"FINISHED"}


class MakeTestShapesOpr(Operator):
    bl_label = "Generate Collection"
    bl_idname = "opr.imgcol_make_testshapes"

    def execute(self, context):
        ImgCol = context.scene.ImgCol
        col_list = context.scene.col_list

        min_size = [ImgCol.min_width, ImgCol.min_height]
        max_size = [ImgCol.max_width, ImgCol.max_height]

        img_list = CreateTestImgs(ImgCol.amount, min_size, max_size)

        name_list = []
        for item in col_list:
            name_list.append(item.name)
        for img in img_list:
            if img.name not in name_list:
                col_list.add()
                col_list[-1].image = img
                col_list[-1].name = img.name
        return {"FINISHED"}


classes = (
    GenerateOpr,
    PreviewOpr,
    RemoveColOpr,
    AddImageOpr,
    RemoveImageOpr,
    ClearColOpr,
    MoveItemOpr,
    RemoveOtherImgOpr,
    MakeTestShapesOpr,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
