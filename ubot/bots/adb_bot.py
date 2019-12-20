from ubot.bots.bot import Bot, ACTIVE_MODE, PASSIVE_MODE
from ubot.settings import SIMILARITY_DEFAULT

from ubot.adb_client import ADBClient
from ubot.adb_input_controller import ADBInputController

from ubot.package_loader import Package
from ubot.frame_grabbers import ADBFrameGrabber


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

    def __enter__(self):
        self.adb_client.start_server()

        width, height = self.adb_client.screensize
        self.frame_grabber = ADBFrameGrabber(self.adb_client, self.config, width, height)

        return self

    def __exit__(self, *args, **kwargs):
        self.adb_client.stop_server()

    def tap(self, sprite_or_coord, similarity=None, then_wait=0.7, **kwargs):

        if isinstance(sprite_or_coord, str):
            sprite = self.pkg.sprites[sprite_or_coord]
            similarity = similarity or SIMILARITY_DEFAULT

            region = self.sprite_locator.locate(sprite, self.retrieve_latest_frame(), similarity, return_best=True)

            if region is not None:
                self.input_controller.tap_randomly(*region)
            else:
                raise ADBBotError(f"Sprite '{sprite_or_coord}' not found on screen")

        else:
            self.input_controller.tap_randomly(*sprite_or_coord)

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
