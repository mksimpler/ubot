import numpy as np
import cv2

import os


def extract_region_from_image(image, region_bounding_box):
    x, y, w, h = region_bounding_box
    return image[y:y+h, x:x+w]


def draw_retangle(image, region_bounding_box, color=(0, 0, 255)):
    img_data = image.copy()
    x, y, w, h = region_bounding_box

    cv2.rectangle(img_data, (x, y), (x + w, y + h), color, 2)

    return img_data


def first_or_none(array):
    if hasattr(array, "__iter__"):
        for o in array:
            return o

    return None


def isolate_sprite(image_region_path, output_file_path):
    result_image = None

    for root, directories, files in os.walk(image_region_path):
        for file in files:
            if not file.endswith(".png"):
                continue

            image = cv2.imread(f"{root}/{file}")
            image = np.concatenate((image, np.full((image.shape[0], image.shape[1], 1), 255, dtype="uint8")), axis=2)

            if result_image is None:
                result_image = image
            else:
                height, width, rgba = image.shape

                for i in range(height):
                    for ii in range(width):
                        if not np.array_equal(image[i, ii, :2], result_image[i, ii, :2]):
                            result_image[i, ii, 3] = 0

    if result_image is not None:
        cv2.imwrite(output_file_path, result_image)
    else:
        print("Not found any image")
