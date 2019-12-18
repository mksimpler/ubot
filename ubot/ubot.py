import sys
from threading import Thread

import argparse


__version__ = "2019.12.12"

valid_commands = [
    "launch",
    "visual_debugger"
]


def execute():
    if len(sys.argv) == 1:
        executable_help()
    elif len(sys.argv) > 1:
        if sys.argv[1] == "-h" or sys.argv[1] == "--help":
            executable_help()
        else:
            command = sys.argv[1]

            if command not in valid_commands:
                raise Exception("'%s' is not a valid Micro-bot command." % command)

            command_function_mapping[command](*sys.argv[2:])


def executable_help():
    print(f"\nMicro-bot v{__version__}")
    print("Available Commands:\n")

    for command, description in command_description_mapping.items():
        print(f"{command.rjust(16)}: {description}")

    print("")


def launch(package_path, *args):
    parser = argparse.ArgumentParser()
    parser.add_argument("--visual-debugger", action='store_true')

    args = parser.parse_args(args)

    if args.visual_debugger:
        visual_debugger(as_execute=False)

    from ubot import package_loader

    package = package_loader.load_package(package_path)
    package.execute()


def visual_debugger(as_execute=True):

    def _spawn_app():
        from ubot.visual_debugger_app import VisualDebuggerApp
        VisualDebuggerApp().run()

    if as_execute:
        try:
            from ubot.adb_client import ADBClient
            adb_client = ADBClient()

            adb_client.start_server()

            width, height = adb_client.screensize

            from ubot.config import config

            from ubot.frame_buffer import FrameBuffer
            FrameBuffer.setup(config)

            from ubot.adb_frame_grabber import ADBFrameGrabber
            frame_grabber = ADBFrameGrabber(adb_client, config, width=width, height=height)

            frame_grabber.start()

            return _spawn_app()
        finally:
            frame_grabber.stop()
            adb_client.stop_server()

    thread = Thread(
        name="visual_debugger_app",
        target=_spawn_app
    )

    thread.start()


command_function_mapping = {
    "help": executable_help,
    "launch": launch,
    "visual_debugger": visual_debugger
}

command_description_mapping = {
    "help": "Print this to console",
    "launch": "Launch package",
    "visual_debugger": "Launch the visual debugger"
}
