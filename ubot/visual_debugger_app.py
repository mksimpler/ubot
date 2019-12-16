try:
    from kivy.config import Config

    Config.set("graphics", "width", 800)
    Config.set("graphics", "height", 600)

    from kivy.app import App

    from kivy.core.window import Window
    from kivy.core.image import Image as CoreImage

    from kivy.uix.widget import Widget
    from kivy.uix.image import Image
    from kivy.uix.label import Label

    from kivy.uix.floatlayout import FloatLayout
    from kivy.uix.gridlayout import GridLayout
    from kivy.uix.boxlayout import BoxLayout

    from kivy.clock import Clock

    from PIL import Image as PILImage
except ImportError:
    raise Exception("Setup has not been been performed for the GUI module.")

from ubot.frame_buffer import FrameBuffer

import io


class VisualDebuggerApp(App):

    def __init__(self, buckets=None):
        super().__init__()
        self.canvas = None

    def build(self):
        self.canvas = VisualDebuggerCanvas(buckets=["0", "1", "2", "3"])

        Clock.schedule_interval(self.update_image_data, 0.01)

        return self.canvas

    def update_image_data(self, *args):
        for i, frame in enumerate(FrameBuffer.get_instance().frames[:self.canvas.bucket_size]):
            self.canvas.update(str(i), frame)


class VisualDebuggerCanvas(Widget):

    def __init__(self, buckets=None):
        super().__init__()

        self.images = dict()

        self.root = FloatLayout(size=(Window.width, Window.height))
        self.grid = GridLayout(cols=8)

        self.add_widget(self.root)
        self.root.add_widget(self.grid)

        for i, bucket in enumerate(buckets):
            layout = BoxLayout(orientation="vertical")

            image = VisualDebuggerImage(
                allow_stretch=False
            )

            image.bind(texture=image.update_texture_filters)

            self.images[bucket] = image

            layout.add_widget(image)

            label = Label(
                text=bucket,
                color=(1, 1, 1, 1),
                size_hint=(1, 0.1)
            )

            layout.add_widget(label)

            self.grid.add_widget(layout)

        self.bucket_size = len(buckets)

        Window.bind(on_resize=self.on_window_resize)
        Window.clearcolor = (0.136, 0.191, 0.25, 1)

    def update(self, bucket, image_data):
        image = PILImage.fromarray(image_data).convert("L")
        image_file = io.BytesIO()

        image.save(image_file, "png")
        image_file.seek(0)

        core_image = CoreImage(image_file, ext="png")
        self.images[bucket].texture = core_image.texture

    def on_window_resize(self, window, width, height):
        self.root.size = (width, height)


class VisualDebuggerImage(Image):

    def update_texture_filters(self, image, texture):
        if not texture:
            return

        texture.min_filter = 'nearest'
        texture.mag_filter = 'nearest'
