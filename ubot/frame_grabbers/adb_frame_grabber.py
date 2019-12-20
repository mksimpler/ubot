from threading import Thread
from time import time, sleep

import posixpath
from os import path

import numpy
import cv2

from ubot.frame import Frame
from ubot.frame_buffer import FrameBuffer
from ubot.frame_limiter import FrameLimiter


class ADBFrameGrabberError(BaseException):
    pass


class ADBFrameGrabber:

    def __init__(self, adb_client, config, width=1280, height=720, fps=30):

        self.adb_client = adb_client
        self.created_time = time()

        self.screen_width = width
        self.screen_height = height

        self.frame_limiter = FrameLimiter(fps=fps)
        self.frame_buffer = FrameBuffer.get_instance()

        self.is_running = False
        self.worker = None

        self.shared_dirs = config["Emulator"]["SharedFolders"]

    def start(self):

        if self.is_running:
            return

        def _worker():
            while self.is_running:
                self.frame_limiter.start()

                frame = self.grab_frame()
                self.frame_buffer.add_frame(frame)

                self.frame_limiter.stop_and_delay()

        self.is_running = True

        self.worker = Thread(
            name="frame-grabber-worker",
            target=_worker
        )

        self.worker.start()

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.worker.join()

    def grab_frame(self):
        frame_data = None

        if self.shared_dirs is None:
            frame_data = cv2.imdecode(
                numpy.asarray(self.adb_client.screencap, dtype=numpy.uint8),
                0
            )
        else:
            dev_path, pc_path = self.shared_dirs
            current_time = time()
            screen_filename = "screen-{0:.2f}.dump".format(current_time - self.created_time)
            dev_path = posixpath.join(dev_path, screen_filename)
            pc_path = path.join(pc_path, screen_filename)

            try:
                self.adb_client.shell(f"screencap {dev_path}")
                with open(pc_path, "rb") as file_dump:
                    buffer = file_dump.read()[12:]
                    header = (self.screen_height, self.screen_width, 4)

                    frame_data = numpy.frombuffer(buffer, dtype=numpy.uint8).reshape(header)
                    frame_data = cv2.cvtColor(frame_data, cv2.COLOR_RGBA2GRAY)

            finally:
                self.adb_client.shell(f"rm {dev_path}")

        previous_frame = self.frame_buffer.previous_frame
        return Frame(frame_data, previous_frame=previous_frame)
