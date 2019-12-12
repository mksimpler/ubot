from kivy.app import App

from kivy.uix.widget import Widget


class VisualDebuggerApp(App):

    def __init__(self):
        super().__init__()

    def build(self):
        self.canvas = VisualDebuggerCanvas()
        return self.canvas


class VisualDebuggerCanvas(Widget):

    def __init__(self):
        super().__init__()
