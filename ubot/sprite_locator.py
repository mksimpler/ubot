import numpy
import cv2

from ubot.coordinates import as_coordinate


class SpriteLocator:

    def __init__(self, **kwargs):
        pass

    def locate_in_region(self, sprite=None, screen_frame=None, threshold=None, return_best=False, screen_region=None, use_global_location=True):
        region_or_list = self.locale(sprite, screen_frame, threshold, return_best)

        if screen_region is None:
            return region_or_list

        if use_global_location:
            screen_region = as_coordinate(screen_region)
            return screen_region.traslate(region_or_list) if return_best else \
                    [screen_region.traslate(region) for region in region_or_list]

        return region_or_list

    def locate(self, sprite=None, screen_frame=None, threshold=None, return_best=False):
        frame = screen_frame.image_data
        match_locations = cv2.matchTemplate(frame, sprite.image_data, cv2.TM_CCOEFF_NORMED)
        _, width, height = sprite.image_data.shape[::-1]

        if return_best:
            _, similarity, _, location = cv2.minMaxLoc(match_locations)

            region = (
                int(location[0]),
                int(location[1]),
                width,
                height
            )

            if isinstance(threshold, (int, float)):
                return None if similarity < threshold else region

            return similarity, region

        else:

            if isinstance(threshold, (int, float)):
                match_locations = numpy.where(match_locations >= threshold)

            regions = []

            for location in zip(*locations[::-1]):

                region = (
                    int(location[0]),
                    int(location[1]),
                    width,
                    height
                )

                regions.append(region)

            return regions


def _filter_similar_coords(coords, distance):
    """
    Filters out coordinates that are close to each other.

    Args:
        coords (array): An array containing the coordinates to be filtered.

    Returns:
        array: An array containing the filtered coordinates.
    """

    filtered_coords = []

    if len(coords) > 0:
        filtered_coords.append(coords[0])
        for coord in coords:
            if as_coordinate(coord).find_closest(filtered_coords)[0] > distance:
                filtered_coords.append(coord)

    return filtered_coords
