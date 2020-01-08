import threading
import types
from queue import Queue


class Task(threading.Thread):

    def __init__(self, **kwargs):

        # process parameters
        args = (self,) + kwargs.get("args", tuple())
        kwargs["args"] = args

        super().__init__(**kwargs)
        self.stop_event = threading.Event()

        self.localock = threading.Lock()
        self.channel = Channel()

    def stop(self):
        self.stop_event.set()

    @property
    def alive(self):
        return not self.stop_event.is_set()

    @property
    def state(self):
        return "alive" if self.alive else "killed"


class TaskError(BaseException):
    pass


class TaskManager:

    tasks = dict()

    @classmethod
    def create_task(cls, name, *args, **kwargs):
        if cls.tasks.get(name, None) is not None:
            raise TaskError(f"Task with name '{name}' has been declared")

        kwargs["name"] = name

        task = Task(*args, **kwargs)

        cls.tasks[name] = task

        return task

    @classmethod
    def get_task(cls, name):
        return cls.tasks.get(name, None)

    @classmethod
    def stop_task(cls, name, join=False):
        task = cls.get_task(name)

        if task is None:
            raise TaskError(f"Task '{name}' is not found")

        task.stop()

        if join:
            task.join()

    @classmethod
    def current_task(cls):
        name = threading.current_thread().name
        return cls.get_task(name)


class Channel:

    def __init__(self, size=1):
        self._receive_ent = threading.Event()
        self._queue = Queue(maxsize=size)


    @property
    def full(self):
        return self._queue.full()


    @property
    def empty(self):
        return self._queue.empty()


    def send(self, data):
        self._queue.put(data, block=True)

        if self._receive_ent.is_set():
            self._receive_ent.clear()

        if self.full:
            self._receive_ent.wait()


    def receive(self):
        data = self._queue.get(block=True)
        self._receive_ent.set()

        return data
