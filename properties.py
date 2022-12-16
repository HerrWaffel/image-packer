import bpy
from bpy.props import (
    IntProperty,
    EnumProperty,
    BoolProperty,
    StringProperty,
    PointerProperty,
    CollectionProperty,
    FloatVectorProperty,
    IntVectorProperty,
)


class ImgCol_Images(bpy.types.PropertyGroup):
    """Group of properties representing an item in the list."""
    image: PointerProperty(
        name="Image",
        type=bpy.types.Image)


class ImgCol_Properties(bpy.types.PropertyGroup):
    packing_modes = [
        ('square_packing', "Square Packing", 
        "Keeps the images in order of the collection list, scales all images to the same size and makes a 1:1 square collection image."),
        ('auto_sort', "Auto Sort", 
        "Keeps the size of the images but doesn't follow the order of the collection list."),
        ('row_packing', "Row Packing", 
        "Keeps the images in order of the collection list and scales images to have the same width or height."),
    ]

    packing_mode: EnumProperty(
        name="Packing Mode",
        items=packing_modes,
        description="Change the packing method of placing images in the collection."
    )
    # row_packing_modes = [
    #     ('med_w', "Median Width", "", 1),
    #     ('med_h', "Median Height", "", 2),
    #     ('avg_w', "Average Width", "", 3),
    #     ('avg_h', "Average Height", "", 4),
    #     ('min_w', "Minimal Width", "", 5),
    #     ('min_h', "Minimal Height", "", 6),
    #     ('max_w', "Maximal Width", "", 7),
    #     ('max_h', "Maximal Height", "", 8),
    # ]

    side: EnumProperty(
        name="Static Side",
        items=[
        ('width', "Width", "Width"),
        ('height', "Height", "Height"),
        ],
        description="Scales images based on the selected side mode."
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
        description="Sets the length of the side and scales images based on aspect ratio."
    )

    # Name
    col_name: StringProperty(
        name="Name",
        default="New Collection"
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
        min=0
    )

    img_size: IntProperty(
        name="Image Size",
        default=512,
        min=1,
        step=1,
        description="The width and height of each image in the collection."
    )

    side_length: IntProperty(
        name="Side Length",
        default=512,
        min=1,
        step=1,
        description="The length of the width/height for each image in the collection."
    )

    # Random
    random_order: BoolProperty(
        name="Random Order",
        default=False,
        description="Places marked images randomly in the collection"
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
    ImgCol_Images,
    ImgCol_Properties,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.ImgCol = PointerProperty(type=ImgCol_Properties)

    bpy.types.Scene.col_list = CollectionProperty(type=ImgCol_Images)
    bpy.types.Scene.col_list_index = IntProperty(name="Index for col_list",
                                                 default=0)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.ImgCol
    del bpy.types.Scene.col_list
    del bpy.types.Scene.col_list_index
