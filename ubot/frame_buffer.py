class FrameBufferError(BaseException):
    pass

class FrameBuffer:

    config = None
    instance = None

    def __init__(self, size=5):
        self.size = size
        self.frames = list()

    @property
    def full(self):
        return len(self.frames) >= self.size

    @property
    def latest_frame(self):
        while len(self.frames) == 0:
            pass # wait

        return self.frames[0]

    @property
    def previous_frame(self):
        return self.frames[0] if len(self.frames) else None

    def add_frame(self, frame):
        if self.full:
            self.frames = [frame] + self.frames[:-1]
        else:
            self.frames = [frame] + self.frames

    @classmethod
    def setup(cls, config):
        cls.config = config

    @classmethod
    def get_instance(cls):
        if cls.config is None:
            raise FrameBufferError("Frame buffer need to be setup before using")

        if cls.instance is None:
            cls.instance = FrameBuffer(size=cls.config["FrameBuffer"]["Size"])

        return cls.instance
