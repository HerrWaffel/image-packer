import bpy
import numpy as np

from math import ceil, floor, sqrt
from operator import mod
from .utils import median_of_list
from mathutils import Color


def remove_imgs(imgs):
    for img in imgs:
        bpy.data.images.remove(img)


def get_srgba_bg_color():
    bg_linear_RGBA = bpy.context.scene.image_packer.bg_color
    RGB = bg_linear_RGBA[:-1]
    color = Color(RGB).from_scene_linear_to_srgb()
    return (color[0], color[1], color[2], bg_linear_RGBA[3])


def make_packed_image(name, size):
    if name in bpy.data.images:
        packed_image = bpy.data.images[name]
        packed_image.scale(size[0], size[1])
    else:
        packed_image = bpy.data.images.new(name, width=size[0], height=size[1])

    # prepare packed_pixels array
    packed_pixels = np.ones((size[1], size[0], 4), 'f')
    packed_pixels[:, :, :] = get_srgba_bg_color()

    return packed_image, packed_pixels


def update_col_pixels(packed_image, packed_pixels, imgs, imgs_pos):
    packed_h = packed_image.size[1]

    for i in range(len(imgs)):
        img = imgs[i]
        w, h = img.size
        x, y = imgs_pos[i]
        
        img_pixels = np.ones((h, w, 4), 'f')
        img.pixels.foreach_get(img_pixels.ravel())
        packed_pixels[packed_h-(y+h): packed_h-y, x: x+w, :4] = img_pixels

    packed_image.pixels.foreach_set(packed_pixels.ravel())
    packed_image.update()


def get_square_imgs_pos(imgs, squares):
    imgs_pos = []
    for i in range(len(imgs)):
        x = mod(i, squares) * imgs[i].size[0]
        y = floor(i / squares) * imgs[i].size[1]
        imgs_pos.append((x, y))
    return imgs_pos


def add_padding_img(img, padding):
    w, h = img.size
    img_pixels = np.ones((h, w, 4), 'f')
    img.pixels.foreach_get(img_pixels.ravel())
    
    w += 2 * padding
    h += 2 * padding
    
    padding_pixels = np.ones((h, w, 4), 'f')
    padding_pixels[:, :, :] = get_srgba_bg_color()
    padding_pixels[padding: h-padding, padding: w-padding] = img_pixels
    
    img.scale(w, h)
    img.pixels.foreach_set(padding_pixels.ravel())
    img.update()
    return


def fill_padding_img(img, padding):
    w, h = img.size
    img_pixels = np.ones((h, w, 4), 'f')
    img.pixels.foreach_get(img_pixels.ravel())
    padding_pixels = np.ones((h + padding[1], w + padding[0], 4), 'f')
    padding_pixels[:, :, :] = get_srgba_bg_color()

    # center the image in the padding
    w_offset = floor(padding[0] / 2)
    h_offset = floor(padding[1] / 2)
    padding_pixels[h_offset: h_offset + h, w_offset: w_offset + w] = img_pixels

    img.scale(w + padding[0], h + padding[1])
    img.pixels.foreach_set(padding_pixels.ravel())
    img.update()
    return


def med_ratio_from_size(sizes):
    ratios = []
    for size in sizes:
        ratios.append(size[0] / size[1])
    return median_of_list(ratios)

def areas_from_size(sizes):
    areas = []
    for size in sizes:
        areas.append(size[0] * size[1])
    return areas


def img_side_length(imgs, image_packer):
    mode = image_packer.side_mode
    row_mode = image_packer.side_switch == "width"

    total_side = []
    for img in imgs:
        total_side.append( img.size[ int(row_mode)])
    
    # set side length based on side mode
    if "med" in mode:
        side = ceil( median_of_list(total_side))
    elif "avg" in mode:
        side = ceil( sum(total_side) / len(total_side))
    elif "min" in mode:
        side = min(total_side)
    elif "max" in mode:
        side = max(total_side)
    else:
        side = image_packer.side_length

    return side


def SquarePacking(packing_list, image_packer):
    padding = image_packer.padding

    side = img_side_length(packing_list, image_packer)
    squares = ceil( sqrt( len(packing_list)))
    max_w = (side + 2*padding) * squares

    temp_imgs = []
    for img in packing_list:
        temp_img = bpy.data.images.new(
            img.name + "_temp", width=img.size[0], height=img.size[1])
        temp_img.pixels[:] = img.pixels

        if image_packer.keep_aspect_ratio:
            w, h = temp_img.size
            scale_factor = min(side / w, side / h)
            new_size = [floor(w * scale_factor), floor(h * scale_factor)]
            fill_padding = [side - new_size[0], side - new_size[1]]
            temp_img.scale(new_size[0], new_size[1])
            fill_padding_img(temp_img, fill_padding)
        else:
            temp_img.scale(side, side)

        add_padding_img(temp_img, padding)
        temp_imgs.append(temp_img)

    imgs_pos = get_square_imgs_pos(temp_imgs, squares)
    col_img, col_pixels = make_packed_image(image_packer.image_pack_name, (max_w, max_w))
    update_col_pixels(col_img, col_pixels, temp_imgs, imgs_pos)
    remove_imgs(temp_imgs)


def RowPacking(packing_list, image_packer, row_mode=True):
    padding = image_packer.padding

    side = img_side_length(packing_list, image_packer)

    # make temp imgs based on side and img aspect ratio
    sizes = []
    temp_imgs = []
    for img in packing_list:
        if row_mode:
            w = ceil(img.size[0] * (side / img.size[1]))
            h = side
        else:
            w = side
            h = ceil((img.size[1] * side) / img.size[0])

        temp_img = bpy.data.images.new(
            img.name + "_temp", width=img.size[0], height=img.size[1])
        temp_img.pixels[:] = img.pixels
        temp_img.scale(w, h)

        w += 2*padding
        h += 2*padding
        sizes.append((w, h))
        
        add_padding_img(temp_img, padding)
        temp_imgs.append(temp_img)
    side += 2*padding

    match image_packer.aspect_ratio_mode:
        case "med":
            ratio = med_ratio_from_size(sizes)
        case "custom":
            ratio = image_packer.aspect_ratio_width / image_packer.aspect_ratio_height

    area = sum(areas_from_size(sizes))
    threshold = ceil( sqrt(area* ratio))
    
    # Initialize the list of image positions
    imgs_pos = []

    # Iterate through the temp_imgs
    if row_mode:
        # Initialize the current position and the maximum width and height
        x = y = 0
        max_w = 0
        for temp_img in temp_imgs:
            w, h = temp_img.size
            # Check if the img fits within the current position
            if x + w > threshold:
                # The img doesn't fit, so start a new line
                x = 0
                y += h
            # The img fits, so place it at the current position
            imgs_pos.append((x, y))
            x += w
            max_w = max(max_w, x)
        max_h = max(imgs_pos, key=lambda x: x[1])[1] + h

    # Keep track of img heights per row to place the next row on.
    # Crop to last row max height to remove empty space.
    else:
        # Calculate the number of images per row
        sides = int((threshold - threshold % side) / side)
        heights = [0] * sides
        for i, temp_img in enumerate(temp_imgs):
            h = temp_img.size[1]
            col_index = i % sides
            width = col_index * side
            height = heights[col_index]

            imgs_pos.append((width, height))
            heights[col_index] += h

        max_w = side * sides
        max_h = max(heights)

    packed_image, packed_pixels = make_packed_image(image_packer.image_pack_name, (max_w, max_h))
    update_col_pixels(packed_image, packed_pixels, temp_imgs, imgs_pos)
    remove_imgs(temp_imgs)


def pack_rectangles(imgs, max_width, max_height):
    x = 0  # Start the current position at (0, 0)
    y = 0
    imgs_pos = []  # Initialize the list of imgs_pos
    row_heights = []  # Initialize the list of row heights
    max_w = 0  # Initialize the maximum width
    max_h = 0  # Initialize the maximum height

    # Iterate through the imgs
    for img in imgs:
        # Check if the img fits within the current position
        if img.size[0] <= max_width - x and img.size[1] <= max_height - y:
            # The img fits, so add its corner to the list
            imgs_pos.append((x, y))
            x += img.size[0]  # Update the current position
            row_heights.append(y + img.size[1])  # Update the row height
            max_w = max(max_w, x)  # Update the maximum width
            max_h = max(max_h, y + img.size[1])  # Update the maximum height
        else:
            # The img doesn't fit, so start a new line
            x = 0
            y = max(row_heights)  # Start the new line at the maximum row height
            imgs_pos.append((x, y))
            x += img.size[0]  # Update the current position
            row_heights.append(y + img.size[1])  # Update the row height
            max_w = max(max_w, x)  # Update the maximum width
            max_h = max(max_h, y + img.size[1])  # Update the maximum height

    # At this point, the imgs_pos list contains the lower left corners of the packed rectangles
    # and max_w and max_h contain the maximum width and height of the packed rectangles
    return imgs_pos, max_w, max_h


def NextFitPacking(packing_list, image_packer):
    sizes = []
    temp_imgs = []
    for img in packing_list:
        temp_img = bpy.data.images.new(
            img.name + "_temp", width=img.size[0], height=img.size[1])
        temp_img.pixels[:] = img.pixels
        add_padding_img(temp_img, image_packer.padding)
        temp_imgs.append(temp_img)

        w, h = temp_img.size
        sizes.append((w, h))
        
    match image_packer.aspect_ratio_mode:
        case "med":
            ratio = med_ratio_from_size(sizes)
        case "custom":
            ratio = image_packer.aspect_ratio_width / image_packer.aspect_ratio_height

    # Amount of area needed to place all pixel data + 50% empty space (cropped later)
    total_area = sum(areas_from_size(sizes))
    area = ceil(total_area * 1.5)  

    max_height = ceil(sqrt(area / ratio))
    max_width = ceil(area / max_height)

    imgs_pos, max_w, max_h = pack_rectangles(temp_imgs, max_width, max_height)
    size = (max_w, max_h)
    packed_image, packed_pixels = make_packed_image(image_packer.image_pack_name, size)
    update_col_pixels(packed_image, packed_pixels, temp_imgs, imgs_pos)
    remove_imgs(temp_imgs)