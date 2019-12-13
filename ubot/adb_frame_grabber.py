from threading import Thread
from time import time, sleep

import posixpath
from os import path

import numpy
import cv2

from ubot.config import config
from ubot.frame_buffer import frame_buffer


class ADBFrameGrabberError(BaseException):
    pass


class ADBFrameGrabber:

    def __init__(self, adb_client, width=1280, height=720, fps=30):

        self.adb_client = adb_client
        self.created_time = time()

        self.screen_width = width
        self.screen_height = height

        self.frame_time = 1 / fps

        self.is_running = False

        self.shared_dirs = config["Emulator"]["SharedFolders"]

    def start(self):

        def _worker():
            while self.is_running:
                cycle_start = time()

                frame = self.grab_frame()
                frame_buffer.add_frame(frame)

                cycle_end = time()

                cycle_duration = (cycle_end - cycle_start)
                cycle_duration -= int(cycle_duration)

                frame_time_left = self.frame_time - cycle_duration

                if frame_time_left > 0:
                    sleep(frame_time_left)

        self.is_running = True

        self.worker = Thread(
            name="frame-grabber-worker",
            target=_worker
        )

        self.worker.start()

    def stop(self):
        self.is_running = False
        self.worker.join()

    def grab_frame(self):
        frame_data = None

        if self.shared_dirs is None:
            frame_data = cv2.imdecode(
                numpy.asarray(self.adb_client.screencap(), dtype=numpy.uint8),
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

            finally:
                self.adb_client.shell(f"rm {dev_path}")

        return frame_data