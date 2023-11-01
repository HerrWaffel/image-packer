import bpy
import random
import numpy as np
import mathutils

from operator import abs


def lerp(x, y, a):
    return(a * x) + ((1-a) * y)


def saturation(r, g, b):
    return (max(r,g,b) - min(r,g,b)) / (max(r,g,b) + 0.000001)


def RGB_lerp(a, b, alpha):
    R = lerp(a[0], b[0], alpha)
    G = lerp(a[1], b[1], alpha)
    B = lerp(a[2], b[2], alpha)
    RGB = mathutils.Vector((R, G, B))
    RGB += mathutils.Vector((0.000001,0,0))

    nR = (2 * R) - G - B
    nG = (2 * G) - R - B
    nB = (2 * B) - G - R
    nRGB = mathutils.Vector((nR, nG, nB))
    nRGB.normalized()
    nRGB = nRGB * nRGB.dot(RGB.normalized())

    sRGB = saturation(R, G, B)
    sA = saturation(a[0],a[1],a[2])
    sB = saturation(b[0],b[1],b[2])
    sAB = lerp(sA, sB, alpha)
    sRGB = abs(sRGB- sAB)

    nRGB *= sRGB
    o = mathutils.Vector((1, 1, 1))
    nRGB *= o.dot(RGB) * 1.5

    out_color = mathutils.Color(nRGB + RGB).from_scene_linear_to_srgb()
    return out_color


def median_of_list(n_list):
    n_list.sort()
    mid = len(n_list) // 2
    return (n_list[mid] + n_list[~mid]) / 2


def get_active_img():
    for area in bpy.context.screen.areas:
        if area.type == 'IMAGE_EDITOR':
            return area.spaces.active.image


def preview_packed_image(packed_image, preview_window):
    if preview_window:
        # Call user prefs window
        bpy.ops.screen.userpref_show('INVOKE_DEFAULT')

        # Change area type
        area = bpy.context.window_manager.windows[-1].screen.areas[0]
        area.type = 'IMAGE_EDITOR'

    # Assign the image
    bpy.context.area.spaces.active.image = packed_image


def shuffle_packing_list(img_list):
    random.seed(bpy.context.scene.image_packer.random_seed)
    return random.shuffle(img_list)


def create_test_imgs(amount, min_size, max_size):
    img_list = []
    random.seed(bpy.context.scene.image_packer.test_seed)
    color_1 = bpy.context.scene.image_packer.end_color
    color_2 = bpy.context.scene.image_packer.start_color

    for i in range(amount):
        name = "testshape_{}".format(i)
        w = random.randint(min_size[0], max_size[0])
        h = random.randint(min_size[1], max_size[1])
        img = bpy.data.images.new(name, width=w, height=h)

        alpha = i / (amount-1)
        mixed = RGB_lerp((color_1[0],color_1[1],color_1[2]), (color_2[0],color_2[1],color_2[2]), alpha)

        img_pixels = np.ones((h, w, 4), 'f')
        img.pixels.foreach_get(img_pixels.ravel())
        img_pixels[:, :, 0] = mixed[0]
        img_pixels[:, :, 1] = mixed[1]
        img_pixels[:, :, 2] = mixed[2]
        img.pixels.foreach_set(img_pixels.ravel())
        img.update()

        img_list.append(img)

    return img_list
