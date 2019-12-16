from ubot.config import config as _config

def make(bot_type=None, config=None, package=None, **kwargs):
    config = config or _config

    if bot_type == "adb":
        from ubot.bots.adb_bot import ADBBot
        return ADBBot(config, package, run_mode=kwargs.get("run_mode", None))

    raise NotImplementedError()
