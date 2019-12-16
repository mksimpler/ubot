from random import randint

from ubot import logger
from ubot.adb_client import ADBServerState as ServerState


class ADBInputControllerError(BaseException):
    pass


class ADBInputController:

    def __init__(self, adb_client, **kwargs):
        self.adb_client = adb_client
        self._screen_frame_mapper = kwargs.get("frame_mapper", None)

    def text(self, string):
        return self.adb_client.device.input_text(string)

    def keyevent(self, keycode, longpress=False):
        return self.adb_client.device.input_keyevent(keycode, longpress)

    def tap(self, x, y):
        if self._screen_frame_mapper is not None:
            x, y = self._screen_frame_mapper(x, y)

        logger.debug(f"Tap [{x}, {y}].")

        return self.adb_client.device.input_tap(x, y)

    def tap_randomly(self, x, y, w, h):
        x = randint(x, x + w)
        y = randint(y, y + h)
        return self.tap(x, y)

    def swipe(self, start_x, start_y, end_x, end_y, duration):
        if self._screen_frame_mapper is not None:
            start_x, start_y = self._screen_frame_mapper(start_x, start_y)
            end_x, end_y = self._screen_frame_mapper(end_x, end_y)

        logger.debug("Swipe from {start} to {end} in {duration}ms.".format(
                start=f"[{start_x}, {start_y}]",
                end=f"[{end_x}, {end_y}]",
                duration=str(duration)
            ))

        return self.adb_client.device.input_swipe(start_x, start_y, end_x, end_y, duration)

    def press(self):
        return self.adb_client.device.input_press()

    def roll(self, dx, dy):
        return self.adb_client.device.roll(dx, dy)
