from ubot.bots.bot import Bot, ACTIVE_MODE, PASSIVE_MODE
from ubot.settings import SIMILARITY_DEFAULT

from ubot.adb_client import ADBClient
from ubot.adb_input_controller import ADBInputController
from ubot.sprite_locator import SpriteLocator

from ubot.frame_buffer import FrameBuffer
from ubot.frame_grabbers import ADBFrameGrabber

from ubot.package_loader import Package


class ADBBotError(BaseException):
    pass


class ADBBot(Bot):

    def __init__(self, config, package, **kwargs):
        super().__init__(config, **kwargs)

        if not isinstance(package, Package):
            raise ValueError("package must be provided")

        self.pkg = package
        self.adb_client = ADBClient()
        self.input_controller = ADBInputController(self.adb_client)
        self.sprite_locator = SpriteLocator()


    def __enter__(self):
        self.adb_client.start_server()
        self._setup_frame_grabber()
        return self

    def __exit__(self, *args, **kwargs):
        self.adb_client.stop_server()

    def seen(self, sprite_name, similarity=None, return_list=False):
        frame = self._retrieve_latest_frame()
        sprite = self.pkg.sprites[sprite_name]
        return self.sprite_locator.locate(sprite, frame, similarity, return_best=not return_list)

    def tap(self, sprite_or_coord, similarity=None, then_wait=0.7):

        if isinstance(sprite_or_coord, str):
            frame = self._retrieve_latest_frame()
            sprite = self.pkg.sprites[sprite_or_coord]
            similarity = similarity or SIMILARITY_DEFAULT

            region = self.sprite_locator.locate(sprite, frame, similarity, return_best=True)

            if region is not None:
                self.input_controller.tap_randomly(*region)
            else:
                raise ADBBotError(f"Sprite '{sprite_or_coord}' not found on screen")

        else:
            self.input_controller.tap_randomly(*coords)

        self.wait(then_wait or 0.7)

    def swipe(self, location_s, location_e, duration, **kwargs):
        """
        Sends an input command to swipe the device screen between the
        specified coordinates via ADB

        Args:
            location_s (Location): Location to begin the swipe at
            location_e (Location): Location to end the swipe at
            duration (int): Duration in miliseconds(ms) of swipe.
        """
        self.input_controller.swipe(*location_s, *location_e, duration)
        self.wait(duration / 1000)

    def text(self):
        pass

    def at_region(self, x, y, w, h):
        return self._retrieve_latest_frame.at_region(x, y, w, h)

    def _setup_frame_grabber(self):
        width, height = self.adb_client.screensize
        self._frame_grabber_ins = ADBFrameGrabber(self.adb_client, self.config, width, height)

    def _retrieve_latest_frame(self):
        frame_buffer = FrameBuffer.get_instance()

        if self.run_flags.get("in_frame_loop", False):
            return frame_buffer.latest_frame

        frame = None

        if self.run_mode == ACTIVE_MODE:
            frame = self.frame_grabber.grab_frame()

        elif self.run_mode == PASSIVE_MODE:
            self.frame_grabber.start()
            frame = frame_buffer.latest_frame

        return frame
