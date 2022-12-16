import bpy
import numpy as np

from math import ceil, floor, sqrt
from operator import mod
from .dependencies import rpack
from .utils import GetMedian
from mathutils import Color


def remove_imgs(imgs):
    for img in imgs:
        bpy.data.images.remove(img)


def get_srgba_bg_color():
    bg_linear_RGBA = bpy.context.scene.ImgCol.bg_color
    RGB = bg_linear_RGBA[:-1]
    color = Color(RGB).from_scene_linear_to_srgb()
    return (color[0], color[1], color[2], bg_linear_RGBA[3])


def make_col_img(col_name, col_size):
    if col_name in bpy.data.images:
        col_img = bpy.data.images[col_name]
        col_img.scale(col_size[0], col_size[1])
    else:
        col_img = bpy.data.images.new(col_name, width=col_size[0], height=col_size[1])

    # prepare col_pixels array
    col_pixels = np.ones((col_size[1], col_size[0], 4), 'f')
    col_pixels[:, :, :] = get_srgba_bg_color()

    return col_img, col_pixels


def update_col_pixels(col_img, col_pixels, imgs, imgs_pos):
    col_h = col_img.size[1]

    for i in range(len(imgs)):
        img = imgs[i]
        w, h = img.size
        x, y = imgs_pos[i]
        
        img_pixels = np.ones((h, w, 4), 'f')
        img.pixels.foreach_get(img_pixels.ravel())
        #img_pixels[:, :, 3] = 1
        col_pixels[col_h-(y+h): col_h-y, x: x+w, :4] = img_pixels

    col_img.pixels.foreach_set(col_pixels.ravel())
    col_img.update()


def get_square_imgs_pos(imgs, col_cells):
    imgs_pos = []
    for i in range(len(imgs)):
        x = mod(i, col_cells) * imgs[i].size[0]
        y = floor(i / col_cells) * imgs[i].size[1]
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


def med_ratio_from_size(sizes):
    ratios = []
    for size in sizes:
        ratios.append(size[0] / size[1])
    return GetMedian(ratios)


def areas_from_size(sizes):
    areas = []
    for size in sizes:
        areas.append(size[0] * size[1])
    return areas


def SquarePacking(img_list, ImgCol):
    size = ImgCol.img_size
    padding = ImgCol.padding

    col_cells = ceil( sqrt( len(img_list)))
    col_size = (size + 2*padding) * col_cells

    temp_imgs = []
    for img in img_list:
        temp_img = bpy.data.images.new(
            img.name + "_temp", width=img.size[0], height=img.size[1])
        temp_img.pixels[:] = img.pixels
        temp_img.scale(size, size)
        add_padding_img(temp_img, padding)
        temp_imgs.append(temp_img)

    imgs_pos = get_square_imgs_pos(temp_imgs,col_cells)
    col_img, col_pixels = make_col_img(ImgCol.col_name, (col_size, col_size))
    update_col_pixels(col_img, col_pixels, temp_imgs, imgs_pos)
    remove_imgs(temp_imgs)


def AutoSort(img_list, ImgCol):
    sizes = []
    temp_imgs = []
    for img in img_list:
        temp_img = bpy.data.images.new(
            img.name + "_temp", width=img.size[0], height=img.size[1])
        temp_img.pixels[:] = img.pixels
        add_padding_img(temp_img, ImgCol.padding)
        temp_imgs.append(temp_img)

        w, h = temp_img.size
        sizes.append((w, h))
        
    # amount of area needed to place all pixel data + 50% empty space
    median_ratio = med_ratio_from_size(sizes) 
    total_area = sum(areas_from_size(sizes))
    area = ceil(total_area * 1.5)  

    max_height = ceil(sqrt(area / median_ratio))
    max_width = ceil(area / max_height)

    imgs_pos = rpack.pack(sizes, max_width, max_height)
    col_size = rpack.bbox_size(sizes, imgs_pos)

    col_img, col_pixels = make_col_img(ImgCol.col_name, col_size)
    update_col_pixels(col_img, col_pixels, temp_imgs, imgs_pos)
    remove_imgs(temp_imgs)


def RowPacking(img_list, ImgCol):
    mode = ImgCol.side_mode
    padding = ImgCol.padding

    height_mode = "height" in ImgCol.side
    
    # fills total_side with height or width of img_list
    total_side = []
    for img in img_list:
        total_side.append( img.size[ int(height_mode)])

    # set side length based on packing mode
    if "med" in mode:
        side = ceil( GetMedian(total_side))
    elif "avg" in mode:
        side = ceil( sum(total_side) / len(total_side))
    elif "min" in mode:
        side = min(total_side)
    elif "max" in mode:
        side = max(total_side)
    else:
        side = ImgCol.side_length

    # make temp imgs based on side and img aspect ratio
    sizes = []
    temp_imgs = []
    for img in img_list:
        temp_img = bpy.data.images.new(
            img.name + "_temp", width=img.size[0], height=img.size[1])
        temp_img.pixels[:] = img.pixels
        
        if height_mode:
            w = ceil(img.size[0] * (side / img.size[1]))
            h = side
        else:
            w = side
            h = ceil((img.size[1] * side) / img.size[0])

        temp_img.scale(w, h)
        add_padding_img(temp_img, padding)
        w += 2*padding
        h += 2*padding
        sizes.append((w, h))
        temp_imgs.append(temp_img)
    side += 2*padding

    # amount of area needed for col pixel data + 50% empty space
    median_ratio = med_ratio_from_size(sizes) 
    total_area = sum(areas_from_size(sizes))
    area = ceil(total_area * 1.5) 
    threshold = ceil( sqrt(area * median_ratio))

    max_w = max_h = 0
    width = height = 0

    # Check if img width > threshold else place img on new row
    # Keep track of max width for cropping empty space
    imgs_pos = []
    if height_mode:
        for i in range(len(temp_imgs)):
            w, h = temp_imgs[i].size
            if width + w > threshold:
                width = w
                max_h += height
                height = h
            else:
                width += w
                height = max(height, h) 
            max_w = max(max_w, width)
            imgs_pos.append((width - w, max_h))
        max_h += height

        col_w = max_w
        col_h = max_h
    
    # Keep track of img heights per row to place the next row on.
    # Crop to last row max height to remove empty space.
    else:
        heights = []
        remainder = mod(threshold,side)
        sides = int((threshold - remainder) / side)
        for i in range(len(temp_imgs)):
            h = temp_imgs[i].size[1]
            col_index = int(mod(i , sides))
            
            width = col_index * side
            height = 0 if (len(heights) < sides) else (heights[col_index])

            imgs_pos.append((width, height))
            
            if (len(heights) < sides):
                heights.append(h)
            else:
                heights[col_index] += h

        col_w = side * sides
        col_h = max(heights)

    col_img, col_pixels = make_col_img(ImgCol.col_name, (col_w, col_h))
    update_col_pixels(col_img, col_pixels, temp_imgs, imgs_pos)
    remove_imgs(temp_imgs)