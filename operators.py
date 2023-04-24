import bpy
from bpy.types import Operator
from .utils import (
    GetActiveImage, 
    shuffle_packing_list, 
    preview_packed_image, 
    CreateTestImgs,
)
from .packing_modes import (
    SquarePacking,
    AutoSort,
    RowPacking,
    NextFitPacking,
)


class GenerateOpr(Operator):
    bl_label = "Generate Packed Image"
    bl_idname = "opr.image_packer_generate"
    bl_description = "Packs all the images from the packing list and generates a new image based on the packing settings"

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer_packing_list
        
    def execute(self, context):
        scene = context.scene
        image_packer = scene.image_packer

        img_list = []
        for img in context.scene.image_packer_packing_list:
            img_list.append(img["image"])

        if image_packer.random_order:
            shuffle_packing_list(img_list)

        match image_packer.packing_mode:
            case "square_packing":
                SquarePacking(img_list, image_packer)
            case "auto_sort":
                AutoSort(img_list, image_packer)
            case "row_packing":
                RowPacking(img_list, image_packer)
            case "nextfit_packing":
                NextFitPacking(img_list, image_packer)
        if GetActiveImage() == None:
            packed_img = bpy.data.images.get(image_packer.image_pack_name)
            bpy.context.area.spaces.active.image = packed_img
        return {"FINISHED"}


class PreviewOpr(Operator):
    bl_label = "Preview Packed Image"
    bl_idname = "opr.image_packer_preview"
    bl_description = "Opens the generated image in the active or new window"

    def execute(self, context):
        scene = context.scene
        image_packer = scene.image_packer

        preview_packed_image(bpy.data.images.get(image_packer.image_pack_name), image_packer.preview_window)
        return {"FINISHED"}


class RemoveColOpr(Operator):
    bl_label = "Remove Packed Image"
    bl_idname = "opr.image_packer_remove"
    bl_description = "Removes the generated based on the name"

    def execute(self, context):
        try:
            bpy.data.images.remove(bpy.data.images.get(
                bpy.context.scene.image_packer.image_pack_name))
        except:
            print("No image found with the name: {}".format(bpy.context.scene.image_packer.image_pack_name))
        return {"FINISHED"}


class AddImageOpr(Operator):
    bl_label = "Add image to packing list"
    bl_idname = "opr.image_packer_add_image"
    bl_description = "Adds the current active image to the packing list"

    def execute(self, context):
        packing_list = context.scene.image_packer_packing_list
        new_image = GetActiveImage()

        name_list = []
        for item in packing_list:
            name_list.append(item.name)

        if new_image.name not in name_list:
            packing_list.add()
            packing_list[-1].image = new_image
            packing_list[-1].name = new_image.name

        return {"FINISHED"}
    

class RemoveImageOpr(Operator):
    bl_label = "Removes image from packing list"
    bl_idname = "opr.image_packer_remove_image"
    bl_description = "Removes the current active image from the packing list"

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer_packing_list

    def execute(self, context):
        packing_list = context.scene.image_packer_packing_list
        index = context.scene.image_packer_packing_list_index

        packing_list.remove(index)
        context.scene.image_packer_packing_list_index = min(
            max(0, index - 1), len(packing_list) - 1)
        
        return {'FINISHED'}


class ClearPackingListOpr(Operator):
    bl_label = "Clear the packing list"
    bl_idname = "opr.image_packer_clear"
    bl_description = "Removes all images from the packing list"

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer_packing_list

    def execute(self, context):
        context.scene.image_packer_packing_list.clear()
        context.scene.image_packer_packing_list_index = 0

        return {'FINISHED'}


class MoveItemOpr(Operator):
    bl_label = "Move an item in the packing list"
    bl_idname = "opr.image_packer_move_item"
    bl_description = "Changes the order of the selected item in the packing list"

    direction: bpy.props.EnumProperty(
        items=(('UP', 'Up', ""),
               ('DOWN', 'Down', ""),
               ))

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer_packing_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        index = bpy.context.scene.image_packer_packing_list
        list_length = len(bpy.context.scene.image_packer_packing_list) - \
            1  # (index starts at 0)
        new_index = index + (-1 if self.direction == 'UP' else 1)

        bpy.context.scene.image_packer_packing_list = max(0, min(new_index, list_length))

    def execute(self, context):
        packing_list = context.scene.image_packer_packing_list
        index = context.scene.image_packer_packing_list

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        packing_list.move(neighbor, index)
        self.move_index()

        return {'FINISHED'}


class RemoveOtherImgOpr(Operator):
    bl_label = "Remove unused images in blend file"
    bl_idname = "opr.image_packer_remove_other_imgs"
    bl_description = "Removes all images in the blend file which are not in the packing list"

    def execute(self, context):
        scene = context.scene

        packing_list = scene.image_packer_packing_list
        name_list = []
        for item in packing_list:
            name_list.append(item.name)

        all_images = bpy.data.images
        for image in all_images:
            if not (image.name in name_list or image.name == scene.image_packer.image_pack_name):
                all_images.remove(image)

        return {"FINISHED"}


class MakeTestShapesOpr(Operator):
    bl_label = "Generates test shapes"
    bl_idname = "opr.image_packer_make_testshapes"
    bl_description = "Makes test shapes and add them to the packing list"

    def execute(self, context):
        image_packer = context.scene.image_packer
        packing_list = context.scene.image_packer_packing_list

        min_size = [image_packer.min_width, image_packer.min_height]
        max_size = [image_packer.max_width, image_packer.max_height]

        img_list = CreateTestImgs(image_packer.amount, min_size, max_size)

        name_list = []
        for item in packing_list:
            name_list.append(item.name)
        for img in img_list:
            if img.name not in name_list:
                packing_list.add()
                packing_list[-1].image = img
                packing_list[-1].name = img.name

        return {"FINISHED"}


classes = (
    GenerateOpr,
    PreviewOpr,
    RemoveColOpr,
    AddImageOpr,
    RemoveImageOpr,
    ClearPackingListOpr,
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
