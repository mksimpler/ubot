from time import time

import numpy
import cv2
import imutils

from ubot.utilities import extract_region_from_image


class ImageError(BaseException):
    pass


class Image:

    def __init__(self, image_data, image_variants=None):
        self.image_data = image_data
        self.image_variants = image_variants or dict()

    @property
    def shape(self):
        shape = self.image_data.shape

        if len(shape) == 2:
            return shape[1], shape[0] # width, height

        elif len(shape) == 3:
            return shape[1], shape[0], shape[2]

        return shape

    @property
    def grayscale(self):
        if "grayscale" not in self.image_variants:
            if len(self.shape) == 2:
                self.image_variants["grayscale"] = self
            else:
                img = cv2.cvtColor(self.image_data, cv2.COLOR_BGR2GRAY)
                self.image_variants["grayscale"] = Image(img)

        return self.image_variants["grayscale"]

    @property
    def threshold(self):
        if "threshold" not in self.image_variants:
            img = self.grayscale.image_data
            img = img - cv2.erode(img, None)
            _, img = cv2.threshold(img, 50, 256, cv2.THRESH_BINARY)
            self.image_variants["threshold"] = Image(img)

        return self.image_variants["threshold"]

    def resize(self, width=None, height=None):
        S_AUTO = "auto"
        width = width or S_AUTO
        height = height or S_AUTO

        variant_name = f"{width}-{height}"

        if variant_name not in self.image_variants:
            if height == S_AUTO:
                img = imutils.resize(self.image_data, width=int(width))
            elif width == S_AUTO:
                img = imutils.resize(self.image_data, height=int(height))
            else:
                img = imutils.resize(self.image_data, width=int(width), height=int(height))

            self.image_variants[variant_name] = Image(img)

        return self.image_variants[variant_name]

    def to_file(self, filepath):
        cv2.imwrite(filepath, self.image_data)

    def extract_region(self, x, y, w, h):
        img_data = extract_region_from_image(self.image_data, (x, y, w, h))
        return Image(img_data)


class Sprite(Image):

    def __init__(self, name, image_data):
        super().__init__(image_data)
        self.name = name

    def append_image_data(self, image_data):
        raise NotImplementedError()

    @staticmethod
    def frompath(path, name=None):
        name = name or re.split(r"[/\\]", path)[-1]
        return Sprite(name, cv2.imread(path))

    @staticmethod
    def frombuffer(buffer, name=None):
        name = name or re.split(r"[/\\]", path)[-1]

        return Sprite(name, cv2.imdecode(
                numpy.asarray(buffer, dtype=numpy.uint8),
                cv2.IMREAD_COLOR
            ))

    @staticmethod
    def resize(sprite, new_name=None, width=None, height=None):
        new_name = new_name or f"{sprite.name}-resized"
        image = sprite.resize(width=width, height=height)
        return Sprite(new_name, image.image_data)

    @staticmethod
    def copy(sprite, new_name=None):
        new_name = new_name or f"{sprite.name}-copy"
        return Sprite(new_name, sprite.image_data.copy())


class Frame(Image):

    def __init__(self, image_data, previous_frame=None, similarity=None):
        super().__init__(image_data)

        self.previous_frame = previous_frame
        if self.previous_frame is not None:
            self._calc_difference()

        if similarity is not None:
            self.similarity = similarity

        self.timestamp = time()

    def _calc_difference(self):
        matches = cv2.matchTemplate(self.image_data, self.previous_frame.image_data, cv2.TM_CCOEFF_NORMED)
        _, similarity, _, _ = cv2.minMaxLoc(matches)

        self.similarity = similarity
