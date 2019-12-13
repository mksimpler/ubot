class FrameBuffer:

    def __init__(self, size=5):
        self.size = size
        self.frames = list()

    @property
    def full(self):
        return len(self.frames) >= self.size

    @property
    def previous_frame(self):
        return self.frames[0] if len(self.frames) else None

    def add_frame(self, frame):
        if self.full:
            self.frames = [frame] + self.frames[:-1]
        else:
            self.frames = [frame] + self.frames


frame_buffer = FrameBuffer()
