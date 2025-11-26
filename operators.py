import bpy
from bpy.types import Operator
from bpy.props import StringProperty
from .utils import (
    get_active_img, 
    shuffle_packing_list, 
    preview_packed_image, 
    create_test_imgs,
)
from .packing_modes import (
    SquarePacking,
    RowPacking,
    NextFitPacking,
)


class GenerateOpr(Operator):
    bl_label = "Generate Packed Image"
    bl_idname = "opr.image_packer_generate"
    bl_description = "Packs all the images from the packing list and generates a new image based on the packing settings"

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer.packing_list
        
    def execute(self, context):
        scene = context.scene
        image_packer = scene.image_packer
        pref = context.preferences.addons[__package__].preferences

        img_list = []
        for img in context.scene.image_packer.packing_list:
            img_list.append(img["image"])

        if image_packer.random_order:
            shuffle_packing_list(img_list)

        match image_packer.packing_mode:
            case "square_packing":
                SquarePacking(img_list, image_packer)
            case "row_packing":
                RowPacking(img_list, image_packer)
            case "col_packing":
                RowPacking(img_list, image_packer, False)
            case "nextfit_packing":
                NextFitPacking(img_list, image_packer)
        
        
        if(pref.auto_open_preview or get_active_img() == None):
            packed_img = bpy.data.images.get(image_packer.image_pack_name)
            bpy.context.area.spaces.active.image = packed_img
        return {"FINISHED"}


class PreviewOpr(Operator):
    bl_label = "Preview Packed Image"
    bl_idname = "opr.image_packer_preview"
    bl_description = "Opens the generated image in the active or new window"

    @classmethod
    def poll(cls, context):
        return bpy.data.images.get(context.scene.image_packer.image_pack_name) is not None
    
    def execute(self, context):
        scene = context.scene
        image_packer = scene.image_packer
        pref = context.preferences.addons[__package__].preferences

        preview_packed_image(bpy.data.images.get(image_packer.image_pack_name), pref.preview_window)

        return {"FINISHED"}


class RemovePackedOpr(Operator):
    bl_label = "Remove Packed Image"
    bl_idname = "opr.image_packer_remove"
    bl_description = "Removes the packed image based on the name"

    @classmethod
    def poll(cls, context):
        return bpy.data.images.get(context.scene.image_packer.image_pack_name) is not None
    
    def execute(self, context):
        bpy.data.images.remove(bpy.data.images.get(
            context.scene.image_packer.image_pack_name))

        return {"FINISHED"}

# Packing List Operators
class AddToPackingListOpr(Operator):
    bl_label = "Add to packing list"
    bl_idname = "opr.add_to_packing_list"
    bl_description = "Adds the current active image to the packing list"

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer.packing_list != None

    def execute(self, context):
        list = context.scene.image_packer.packing_list
        pref = context.preferences.addons[__package__].preferences
        new_item = get_active_img()

        if new_item is None:
            self.report({'INFO'}, "Open an image in the Image Editor to add to the Packing List")
            return {"CANCELLED"}
        
        # If duplicates are allowed or the new item is not in the packing list 
        if pref.allow_duplicates or new_item.name not in [item.name for item in list]:
            item = list.add()
            item.name = new_item.name
            item.image = new_item
            # Set the packing_list_index to the index of the last item in the list
            context.scene.image_packer.packing_list_index = len(list) - 1

        return {"FINISHED"}

class RemoveFromPackingListOpr(Operator):
    bl_label = "Remove from packing list"
    bl_idname = "opr.remove_from_packing_list"
    bl_description = "Removes the current active image from the packing list"

    @classmethod
    def poll(cls, context):
        """Checks whether the packing list exists and has items"""
        return context.scene.image_packer.packing_list != None and len(context.scene.image_packer.packing_list) > 0

    def execute(self, context):
        list = context.scene.image_packer.packing_list
        index = context.scene.image_packer.packing_list_index

        list.remove(index)
        context.scene.image_packer.packing_list_index = min(max(0, index - 1), len(list))

        return {'FINISHED'}

class ClearPackingListOpr(Operator):
    bl_label = "Clear packing list"
    bl_idname = "opr.clear_packing_list"
    bl_description = "Removes all images from the packing list"

    @classmethod
    def poll(cls, context):
        """Checks whether the packing list exists and has items, and returns a boolean"""
        return context.scene.image_packer.packing_list != None and len(context.scene.image_packer.packing_list) > 0

    def execute(self, context):
        # Get the specified list from the current scene
        list = context.scene.image_packer.packing_list

        # Clear the list
        list.clear()
        self.report({'INFO'}, "Cleared Packing List")

        # Set index of the list to 0
        context.scene.image_packer.packing_list_index = 0

        return {'FINISHED'}

class MoveItemOpr(Operator):
    bl_label = "Move an item in the packing list"
    bl_idname = "opr.image_packer_move_item"
    bl_description = "Changes the order of the selected image in the packing list"

    direction: bpy.props.EnumProperty(
        items=(('UP', 'Up', ""),
               ('DOWN', 'Down', ""),
               ))

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer.packing_list

    def move_index(self):
        """ Move index of an item render queue while clamping it. """

        list_length = len(bpy.context.scene.image_packer.packing_list) - 1  # (index starts at 0)
        index = bpy.context.scene.image_packer.packing_list_index
        new_index = index + (-1 if self.direction == 'UP' else 1)

        new_index = max(0, min(new_index, list_length))
        bpy.context.scene.image_packer.packing_list_index = new_index

    def execute(self, context):
        packing_list = context.scene.image_packer.packing_list
        index = context.scene.image_packer.packing_list_index

        neighbor = index + (-1 if self.direction == 'UP' else 1)
        packing_list.move(neighbor, index)
        self.move_index()

        return {'FINISHED'}


# Extra Options
class RemoveOtherImgOpr(Operator):
    bl_label = "Remove unused images in blend file"
    bl_idname = "opr.image_packer_remove_other_imgs"
    bl_description = "Removes all unused images in the blend file, excluding the packed image"

    def execute(self, context):
        for image in bpy.data.images:
            if (image.users == 0 and image.name != context.scene.image_packer.name):
                bpy.data.images.remove(image)

        return {"FINISHED"}

class AddAllImgOpr(Operator):
    bl_label = "Adds all images to packing list"
    bl_idname = "opr.image_packer_add_all_imgs"
    bl_description = "Add all images in the blend file to the packing list, excluding the packed image"

    @classmethod
    def poll(cls, context):
        return context.scene.image_packer.packing_list != None

    def execute(self, context):
        list = context.scene.image_packer.packing_list
        pref = context.preferences.addons[__package__].preferences

        for image in bpy.data.images:
            new_item = image
            not_packing_img = new_item.name != context.scene.image_packer.name

            # If duplicates are allowed or the new item is not in the packing list 
            if  not_packing_img and (pref.allow_duplicates or new_item.name not in [item.name for item in list]):
                item = list.add()
                item.name = new_item.name
                item.image = new_item
                # Set the packing_list_index to the index of the last item in the list
                context.scene.image_packer.packing_list_index = len(list) - 1
            
        return {"FINISHED"}

class MakeTestShapesOpr(Operator):
    bl_label = "Generates test shapes"
    bl_idname = "opr.image_packer_make_testshapes"
    bl_description = "Makes test shapes and add them to the packing list"

    def execute(self, context):
        image_packer = context.scene.image_packer
        packing_list = context.scene.image_packer.packing_list

        min_size = [image_packer.min_width, image_packer.min_height]
        max_size = [image_packer.max_width, image_packer.max_height]

        img_list = create_test_imgs(image_packer.amount, min_size, max_size)

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
    RemovePackedOpr,
    AddToPackingListOpr,
    RemoveFromPackingListOpr,
    ClearPackingListOpr,
    MoveItemOpr,
    RemoveOtherImgOpr,
    AddAllImgOpr,
    MakeTestShapesOpr,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
