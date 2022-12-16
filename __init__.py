bl_info = {
    "name": "Generate Image Collection",
    "description": "Add images to a collection and generate a image of the collection",
    "author": "Quint Vrolijk",
    "version": (1, 0, 0),
    "blender": (3, 0, 0),
    "location": "Image Editor",
    "category": "Paint"
}

import importlib
from . import operators, properties, ui
from .dependencies import rpack


modules = [
	rpack,
]

def register():
	# reload the submodules
	for module in modules:
		importlib.reload(module)

	properties.register()
	operators.register()
	ui.register()

def unregister():
	ui.unregister()
	operators.unregister()
	properties.unregister()

if __name__ == "__main__":
    register()