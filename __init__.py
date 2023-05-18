bl_info = {
    "name": "Image Packer",
    "description": "Combine multiple images into a single image using different packing algorithms",
    "author": "Quint Vrolijk",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Image Editor",
    "category": "Paint"
}

import importlib
from . import operators, properties, ui, preferences
from .dependencies import rpack


modules = [
	rpack,
]

def register():
	# reload the submodules
	for module in modules:
		importlib.reload(module)

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