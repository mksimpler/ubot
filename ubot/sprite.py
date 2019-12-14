import re
import numpy
import cv2

from ubot.coordinates import as_coordinate


class SpriteError(BaseException):
    pass


class Sprite:

    def __init__(self, name, image_data):
        self.name = name
        self.image_data = image_data

    @property
    def shape(self):
        return self.image_data.shape[::-1]

    def append_image_data(self, image_data):
        raise NotImplementedError()

    @staticmethod
    def from_path(path, name=None):
        name = name or re.split(r"[/\\]", path)[-1]
        return Sprite(name, cv2.imread(path, 0)[..., numpy.newaxis])

    @staticmethod
    def from_buffer(buffer, name=None):
        name = name or re.split(r"[/\\]", path)[-1]

        return Sprite(name, cv2.imdecode(
                numpy.asarray(buffer, dtype=numpy.uint8),
                0
            )[..., numpy.newaxis])

    @staticmethod
    def to_file(cls, sprite, path):
        cv2.imwrite(path, sprite.image_data)

    @staticmethod
    def resize(sprite, new_name=None, new_size=None, scale=None):
        new_name = new_name or f"{sprite.name}-resized"

        if new_size is not None:
            return Sprite(new_name, cv2.resize(sprite.image_data, new_size, interpolation=cv2.INTER_LINEAR))

        if scale is not None:
            return Sprite(new_name, None, fx=scale, fy=scale)

        return sprite

    @staticmethod
    def copy(sprite, new_name=None):
        new_name = new_name or f"{sprite.name}-copy"
        return Sprite(new_name, sprite.image_data.copy())
