from time import time
import cv2


class Frame:

    def __init__(self, image_data, previous_frame=None, similarity=None):
        self.image_data = image_data

        self.previous_frame = previous_frame
        if self.previous_frame is not None:
            self._calc_difference()

        self.similarity = similarity

        self.timestamp = time()

    def at_region(self, x, y, w, h):
        return Frame(self.image_data[x:x+w, y:y+h])

    def to_file(self, filepath):
        cv2.imwrite(filepath, self.image_data)

    @staticmethod
    def resize(frame, new_size=None, scale=None):
        if new_size is not None:
            return Frame(cv2.resize(frame.image_data, new_size, interpolation=cv2.INTER_LINEAR))

        if scale is not None:
            return Frame(cv2.resize(frame.image_data, None, fx=scale, fy=scale, interpolation=cv2.INTER_LINEAR))

    def _calc_difference(self):
        matches = cv2.matchTemplate(self.image_data, self.previous_frame.image_data, cv2.TM_CCOEFF_NORMED)
        _, similarity, _, _ = cv2.minMaxLoc(matches)

        self.similarity = similarity
