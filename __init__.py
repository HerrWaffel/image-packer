bl_info = {
    "name": "Image Packer",
    "description": "Combine multiple images into a single image using different packing algorithms",
    "author": "Quint Vrolijk",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Image Editor",
    "category": "Paint"
}

from . import operators, properties, ui, preferences


def register():
	preferences.register()
	properties.register()
	operators.register()
	ui.register()

def unregister():
	ui.unregister()
	operators.unregister()
	properties.unregister()
	preferences.unregister()

if __name__ == "__main__":
    register()