from time import sleep
from random import uniform

from ubot import logger
from ubot.frame_buffer import FrameBuffer
from ubot.frame_limiter import FrameLimiter


ACTIVE_MODE = "active"
PASSIVE_MODE = "passive"


class BotError(BaseException):
    pass


class Bot:

    def __init__(self, config, **kwargs):
        run_mode = kwargs.get("run_mode", None)
        self.config = config
        self.run_flags = dict()
        self.run_mode = run_mode if run_mode in [ACTIVE_MODE, PASSIVE_MODE] else ACTIVE_MODE

        self._frame_grabber_ins = None
        self._setup_frame_buffer()

    @property
    def frame_grabber(self):
        if self._frame_grabber_ins is None:
            raise NotImplementedError()

        return self._frame_grabber_ins

    def wait(self, duration=None, flex=None):
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
        step_idx = _find_step_idx(steps, starting_step)

        if step_idx is None:
            step_idx = 0

        if not isinstance(data_hub, dict):
            data_hub = dict()

        previous_step_idx = None

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

            next_step_idx = _find_step_idx(steps, next_step_idx)
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
                    frame = FrameBuffer.get_instance().latest_frame
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

    def _setup_frame_buffer(self):
        FrameBuffer.setup(self.config)


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
            found_steps = [i for i, s in enumerate(steps) if s.name == value]
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
