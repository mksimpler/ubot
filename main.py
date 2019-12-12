import sys

__version__ = "2019.12.12"

valid_commands = [
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


def visual_debugger():
    from ubot.visual_debugger.visual_debugger_app import VisualDebuggerApp
    VisualDebuggerApp().run()


command_function_mapping = {
    "visual_debugger": visual_debugger
}

command_description_mapping = {
    "visual_debugger": "Launch the visual debugger"
}

if __name__ == "__main__":
    execute()
