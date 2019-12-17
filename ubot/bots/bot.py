from time import sleep
from random import uniform
import inspect

from ubot import logger
from ubot.frame_buffer import FrameBuffer
from ubot.frame_limiter import FrameLimiter

from ubot.settings import SIMILARITY_DEFAULT
from ubot.sprite_locator import SpriteLocator
from ubot.ocr import detect_numbers


ACTIVE_MODE = "active"
PASSIVE_MODE = "passive"


class BotError(BaseException):
    pass


class Bot:

    def __init__(self, config, **kwargs):
        self.config = config

        self.run_flags = dict()

        run_mode = kwargs.get("run_mode", None)
        self.run_mode = run_mode if run_mode in [ACTIVE_MODE, PASSIVE_MODE] else ACTIVE_MODE

        self.frame_grabber = None

        self.frame_buffer = None
        self._setup_frame_buffer()

        self.sprite_locator = SpriteLocator()

    @property
    def latest_frame(self):
        if self.run_flags.get("in_frame_loop", False):
            return self.frame_buffer.latest_frame

        frame = None

        if self.run_mode == ACTIVE_MODE:
            frame = self.frame_grabber.grab_frame()
            self.frame_buffer.add_frame(frame)

        elif self.run_mode == PASSIVE_MODE:
            self.frame_grabber.start()
            frame = self.frame_buffer.latest_frame

        return frame

    def seen(self, *sprite_names, similarity=SIMILARITY_DEFAULT, best_match=True, dont_update_screen=False, return_dict=False, **kwargs):
        if dont_update_screen:
            frame = self.frame_buffer.previous_frame
        else:
            frame = self.latest_frame

        sprite_names = sprite_names[0] if isinstance(sprite_names[0], (list, tuple)) else sprite_names
        sprites = [self.pkg.sprites[sprite_name] for sprite_name in sprite_names]
        results = [self.sprite_locator.locate(sprite, frame, similarity, return_best=best_match) for sprite in sprites]

        if len(sprite_names) == 1:
            return results[0]

        if return_dict:
            return dict(zip(sprite_names, results))

        return results

    def wait(self, duration=None, flex=None, **kwargs):
        """
        Method for putting the program to sleep for a random amount of time.
        If base is not provided, defaults to somewhere along with 0.4 and 0.7
        seconds. If base is provided, the sleep length will be between base
        and 2*base. If base and flex are provided, the sleep length will be
        between base and base+flex. The global SLEEP_MODIFIER is than added to
        this for the final sleep length.

        Args:
            base (int, optional): Minimum amount of time to go to sleep for.
            flex (int, optional): The delta for the max amount of time to go
                to sleep for.
        """
        if duration is None:
            sleep(uniform(0.4, 0.7))
        else:
            flex = duration if flex is None else flex
            sleep(uniform(duration, duration + flex))

    def waitfor_image(self, image, fps=2, **kwargs):
        def _handler(frame):
            if self.seen(image, **kwargs):
                return "break"

        self.handle_frame(frame_handler=_handler, fps=fps)

    def waitwhile_image(self, image, fps=2, **kwargs):
        def _handler(frame):
            if not self.seen(image, **kwargs):
                return "break"

        self.handle_frame(frame_handler=_handler, fps=fps)

    def waitfor_frame_stable(self, fps=3, **kwargs):
        def _handler(frame):
            if len(FrameBuffer.get_instance().frames) >= 3:
                frame, previous_frame = FrameBuffer.get_instance().frames[0], FrameBuffer.get_instance().frames[1]
                if frame.similarity > SIMILARITY_DEFAULT and previous_frame.similarity > SIMILARITY_DEFAULT:
                    return "break"

        self.handle_frame(frame_handler=_handler, fps=fps)

    def exec_by_steps(self, steps, starting_step=None, data_hub=None):
        """
        Execute by provided steps

        Parameter
        ---------
        steps
            array of dict

        starting_step
            int or string - optional

        data_hub
            dict - optional
        """
        step_idx = _find_step(steps, starting_step)

        if step_idx is None:
            step_idx = 0

        if not isinstance(data_hub, dict):
            data_hub = dict()

        previous_step = None

        while step_idx < len(steps):
            step = steps[step_idx]

            name = step.get("name", "no-name-step")
            handler = step.get("handler", None)
            args = step.get("args", tuple())
            kwargs = step.get("kwargs", dict())

            if handler is None:
                # skip step
                logger.debug(f"Skip '{name}'.")
                step_idx += 1
                continue

            logger.debug(f"Run '{name}'.")

            args, kwargs = _fill_parameters(handler, args, kwargs,
                params=dict(
                    bot=self,
                    hub=data_hub,
                    previous_step=previous_step
                ))

            try:
                next_step_idx = handler(*args, **kwargs)
            except Exception as ex:
                raise ex

            next_step_idx = _find_step(steps, next_step_idx)
            if next_step_idx is not None:
                step_idx = next_step_idx
            else:
                step_idx += 1

            previous_step = name

        return data_hub

    def handle_frame(self, frame_handler=None, fps=30, **kwargs):

        if not callable(frame_handler):
            if hasattr(frame_handler, "handle_frame") and callable(frame_handler.handle_frame):
                frame_handler = frame_handler.handle_frame
            else:
                raise BotError("frame_handler must be function or frame-agent like instance")

        try:
            frame_limiter = FrameLimiter(fps=fps)

            self.frame_grabber.start()

            self.run_flags["in_frame_loop"] = True

            while True:
                frame_limiter.start()

                try:
                    frame = self.frame_buffer.latest_frame
                    signal = frame_handler(frame, **kwargs)
                except Exception as ex:
                    raise ex

                frame_limiter.stop_and_delay()

                if signal == "break":
                    break

                if signal == "continue":
                    continue

        finally:
            self.run_flags["in_frame_loop"] = False
            self.frame_grabber.stop()

    def detect_numbers(self, image, sprite_name_list, max_digits):
        fonts = [self.pkg.sprites[sprite_name] for sprite_name in sprite_name_list]
        return detect_numbers(image, fonts, max_digits)

    def _setup_frame_buffer(self):
        FrameBuffer.setup(self.config)
        self.frame_buffer = FrameBuffer.get_instance()


def _find_step(steps, value):
    if value is None:
        return None

    n_steps = len(steps)

    if isinstance(value, int):
        # jump to step
        index = 0 if value < 0 else value
        index = len(steps) - 1 if index >= len(steps) else index
        return index

    if isinstance(value, str):
        # find and jump to step
        default_steps = dict(
            begin=0,
            final=n_steps - 1,
            end=n_steps
        )

        if value in default_steps:
            return default_steps[value]

        if value != "":
            found_steps = [i for i, s in enumerate(steps) if s["name"] == value]
            if len(found_steps) == 0:
                raise ValueError(f"Step '{value}' not found.")

            if len(found_steps) > 1:
                logger.warning(f"Step '{value}' has duplicate name.")

            return found_steps[0]

    return None


def _fill_parameters(handler, args, kwargs, params=None):
    # todo: rewrite this stupid buggy method
    params_dict = inspect.signature(handler).parameters

    if "kwargs" in params_dict:
        kwargs["bot"] = params["bot"]
        kwargs["hub"] = params["hub"]
        kwargs["previous_step"] = params["previous_step"]
    else:
        if "bot" in params_dict:
            kwargs["bot"] = params["bot"]

        if "hub" in params_dict:
            kwargs["hub"] = params["hub"]

        if "previous_step" in params_dict:
            kwargs["previous_step"] = params["previous_step"]

    return args, kwargs
