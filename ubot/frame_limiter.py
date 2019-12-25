import time

from datetime import datetime


class FrameLimiter:

    def __init__(self, fps=30):
        self.frame_time = 1 / fps
        self.started_at = None

    def start(self):
        self.started_at = datetime.utcnow()

    def stop_and_delay(self):
        duration = self.runtime
        remaining_frame_time = self.frame_time - duration

        if remaining_frame_time > 0:
            time.sleep(remaining_frame_time)

    @property
    def runtime(self):
        if self.started_at is None:
            return -1

        return (datetime.utcnow() - self.started_at).microseconds / 1000000
