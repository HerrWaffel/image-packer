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

def packing_list_index_callback(self, context):
    packing_list = context.scene.image_packer_packing_list
    index = context.scene.image_packer_packing_list_index
    bpy.context.area.spaces.active.image = packing_list[index].image


class PackItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    image: PointerProperty(
        name="Image",
        type=bpy.types.Image)


class ImagePacker(bpy.types.PropertyGroup):
    packing_modes = [
        ('square_packing', "Square Packing", 
        "Scales all images to the same size and makes a 1:1 packed image, keeps the images in order"),
        ('row_packing', "Row Packing", 
        "Scales images to have the same height, keeps the images in order"),
        ('col_packing', "Column Packing", 
        "Scales images to have the same width, keeps the images in order"),
        ('nextfit_packing', "Next Fit Packing",
        "Keeps the size and order of the images, but may result in gaps between the rows"),
    ]

    packing_mode: EnumProperty(
        name="Mode",
        items=packing_modes,
        description="Change the algorithm for packing the images"
    )

    side_mode: EnumProperty(
        name="Mode",
        items=[
            ('min', "Minimal", "Scale images based on the minimal size (width or height) of all the images"),
            ('max', "Maximal", "Scale images based on the maximal size (width or height) of all the images"),
            ('avg', "Average", "Scale images based on the average size (width or height) of all the images"),
            ('med', "Median", "Scale images based on the median size (width or height) of all the images"),
            ('custom', "Custom", "Scale images based on a custom width or height"),
        ],
        description="Scales images based on the mode to the correct aspect ratio"
    )

    side_switch: EnumProperty(
        name="Side",
        items=[
            ('width', "Width", "Scale images based on the width"),
            ('height', "Height", "Scale images based on the height"),
        ],
        description="Switch between width and height"
    )

    keep_aspect_ratio: BoolProperty(
        name="Keep Aspect Ratio",
        default=True,
        description="Keep the aspect ratio of the images"
    )

    image_pack_name: StringProperty(
        name="Name",
        default="New Packed Image",
        description="The name of the packed image"
    )

    bg_color: FloatVectorProperty(
        name="Background Colour",
        default=(0.5, 0.5, 0.5, 1),
        size=4,
        subtype="COLOR",
        min=0,
        max=1
    )
    
    padding: IntProperty(
        name="Padding",
        default=0,
        min=0,
        description="Add padding to each image in the packing list"
    )

    img_size: IntProperty(
        name="Image Size",
        default=512,
        min=1,
        step=1,
        description="The width and height of each image"
    )

    side_length: IntProperty(
        name="Side Length",
        default=512,
        min=1,
        step=1,
        description="The length of the width/height for each image"
    )

    # Random
    random_order: BoolProperty(
        name="Random Order",
        default=False,
        description="Should the images be placed in order or be randomized"
    )
    random_seed: IntProperty(
        name="Random Seed",
        default=0,
        step=1,
        description="Seed for random order"
    )

    # Test Shapes
    start_color: FloatVectorProperty(
        name="Start Colour",
        default=(0.92, 0.34, 0.1, 1),
        size=4,
        subtype="COLOR",
        min=0,
        max=1
    )
    end_color: FloatVectorProperty(
        name="End Colour",
        default=(0.06, 0.07, 0.1, 1),
        size=4,
        subtype="COLOR",
        min=0,
        max=1
    )
    test_seed: IntProperty(
        name="Shapes Seed",
        default=0,
        step=1,
        description="Seed for random shape sizes"
    )
    min_width: IntProperty(
        name="Min Width",
        default=100,
        min=1,
        step=1
    )
    max_width: IntProperty(
        name="Max Width",
        default=500,
        min=1,
        step=1
    )
    min_height: IntProperty(
        name="Min Height",
        default=100,
        min=1,
        step=1
    )
    max_height: IntProperty(
        name="Max Height",
        default=150,
        min=1,
        step=1
    )
    amount: IntProperty(
        name="Amount",
        default=16,
        min=1,
        step=1
    )


classes = (
    PackItem,
    ImagePacker,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.image_packer = PointerProperty(type=ImagePacker)
    # List of images to pack
    bpy.types.Scene.image_packer_packing_list = CollectionProperty(type=PackItem)
    bpy.types.Scene.image_packer_packing_list_index = IntProperty(name="Index for packing_list",
                                                 default=0,
                                                 update=packing_list_index_callback)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.image_packer
    del bpy.types.Scene.image_packer_packing_list
    del bpy.types.Scene.image_packer_packing_list_index
