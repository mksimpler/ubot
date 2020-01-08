import numpy
import cv2

from ubot import logger
from ubot.coordinates import as_coordinate, filter_similar_coords


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

    # def locate(self, sprite=None, screen_frame=None, threshold=None, return_best=False):
    #     frame = screen_frame.image_data
    #     match_locations = cv2.matchTemplate(frame, sprite.image_data, cv2.TM_CCOEFF_NORMED)
    #     _, width, height = sprite.image_data.shape[::-1]

    #     if return_best or threshold is None:
    #         _, similarity, _, location = cv2.minMaxLoc(match_locations)

    #         region = (
    #             int(location[0]),
    #             int(location[1]),
    #             width,
    #             height
    #         )

    #         if isinstance(threshold, (int, float)):
    #             return None if similarity < threshold else region

    #         return region

    #     else:

    #         match_locations = numpy.where(match_locations >= threshold)

    #         regions = []

    #         for location in zip(*match_locations[::-1]):

    #             region = (
    #                 int(location[0]),
    #                 int(location[1]),
    #                 width,
    #                 height
    #             )

    #             regions.append(region)
    #             regions = filter_similar_coords(regions, 40)

    #         return regions


    def locate(self, sprite, screen_frame, **options):
        '''
        Parameter
        ---------
        sprite:
            Sprite

        screen_frame:
            Frame

        options:
            dict (optional)
                im_mode:
                    string, default(None)
                    Set image processing method before matching. Currently support (threshold,)

                im_scale:
                    float, defaule(None)
                    Set scale of image to be resized then matching with all resized image.

                best_match:
                    bool, default(True)
                    Filter result with only one best match.

                threshold:
                    float, default(Max)
                    Threshold of similarity to be filter. Default to max of similarity if not provided.

        Returns
        -------
        array
            Array of region(x, y, width, height) of found locations
        '''
        templates = []

        if "im_mode" in options:
            im_mode = options["im_mode"]

            if im_mode == "threshold":
                sprite = sprite.threshold
                screen_frame = screen_frame.threshold

            elif im_mode == "grayscale":
                sprite = sprite.grayscale
                screen_frame = screen_frame.grayscale

        if "im_scale" in options:
            im_scale = options["im_scale"]
            tW, tH = (-1, -1)

            for scale in numpy.linspace(im_scale, 1, num=10):
                template = sprite.resize(width=int(sprite.shape[0] * scale))

                if template.shape == (tW, tH):
                    continue
                else:
                    tW, tH = template.shape
                    templates.append(template)

        else:
            templates = [sprite]

        # match template
        get_min_max = options.get("best_match", True)
        threshold = options.get("threshold", None)

        locations = []

        for template in templates:
            result = self._match_template(screen_frame, template, get_min_max=get_min_max, threshold=threshold)
            locations += [r for r in result if r is not None]

        return filter_similar_coords(locations, 10)


    def _match_template(self, frame, template, get_min_max=True, threshold=None):
        ccnorm = cv2.matchTemplate(frame.image_data, template.image_data, cv2.TM_CCOEFF_NORMED)

        if get_min_max:
            _, score, _, location = cv2.minMaxLoc(ccnorm)

            if threshold is None:
                return [(*location, *template.shape[:2])]
            else:
                return [(*location, *template.shape[:2])] if score >= threshold else [None]

        else:
            locations = []

            if threshold is None:
                threshold = ccnorm.max()

            for location in zip(*numpy.where(ccnorm >= threshold)[::-1]):
                locations.append((int(location[0]), int(location[1]), *template.shape[:2]))

            return locations
