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


class PackItem(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    image: PointerProperty(
        name="Image",
        type=bpy.types.Image)


class ImagePacker(bpy.types.PropertyGroup):
    packing_modes = [
        ('square_packing', "Square Packing", 
        "Keeps the images in order of the images list, scales all images to the same size and makes a 1:1 packed image"),
        ('auto_sort', "Auto Sort", 
        "Keeps the size of the images but doesn't follow the order of the images list"),
        ('row_packing', "Row Packing", 
        "Keeps the images in order of the images list and scales images to have the same width or height"),
        ('nextfit_packing', "Next Fit Packing",
        "Keeps the size of the images and follows the order of the images list, but may result in gaps between the rows"),
    ]

    packing_mode: EnumProperty(
        name="Packing Mode",
        items=packing_modes,
        description="Change the algorithm for packing the images"
    )

    side: EnumProperty(
        name="Static Side",
        items=[
        ('width', "Width", "Width"),
        ('height', "Height", "Height"),
        ],
        description="Scales images based on the selected side mode"
    )

    side_mode: EnumProperty(
        name="Mode",
        items=[
        ('min', "Minimal", ""),
        ('max', "Maximal", ""),
        ('avg', "Average", ""),
        ('med', "Median", ""),
        ('custom', "Custom", ""),
        ],
        description="Sets the length of the side and scales images based on aspect ratio"
    )

    image_pack_name: StringProperty(
        name="Name",
        default="New Packed Image"
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
        description="Adds padding to each image in the collection"
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

    preview_window: BoolProperty(
        name="New Preview Window",
        default=False,
        description="Preview the packed image in a new window"
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
                                                 default=0)
    # List of images not to delete from blend file.
    bpy.types.Scene.image_packer_exclude_list = CollectionProperty(type=PackItem)
    bpy.types.Scene.image_packer_exclude_list_index = IntProperty(name="Index for exclude_list",
                                                 default=0)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.image_packer
    del bpy.types.Scene.image_packer_packing_list
    del bpy.types.Scene.image_packer_packing_list_index
    del bpy.types.Scene.image_packer_exclude_list
    del bpy.types.Scene.image_packer_exclude_list_index
