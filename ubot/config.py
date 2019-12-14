from configparser import ConfigParser


_CONFIG_PATH = "config/config.ldplayer.ini"

IPADDR = "127.0.0.1"
SCREEN = "1280x720"
BOOLEAN = "Boolean"
INTEGER = "Integer"
REAL = "Float"
STRING = "String"
ARRAY = "Array"


def _create_parser():
    """
    Create ConfigParser() instance
    """
    parser = ConfigParser()
    parser.optionxform = str
    return parser


def _load_config(config_path):
    """
    Load config file
    """
    parser = _create_parser()
    parser.read(config_path)

    config_model = _create_parser()
    config_model.read_dict({
        "Emulator": {
            "Host": IPADDR,
            "Port": INTEGER,
            "Serial": STRING,
            "ScreenSize": SCREEN,
            "SharedFolders": ARRAY
        },
        "Updates": {
            "Enabled": BOOLEAN,
            "Channel": STRING
        }
    })

    config = {
        "Emulator": {
            "Host": "127.0.0.1",
            "Port": 5037,
            "Serial": None,
            "ScreenSize": "1280x720",
            "SharedFolders": None
        },
        "Updates": {
            "Enabled": True,
            "Channel": "Release"
        }
    }

    for section in parser.sections():
        config_section = config[section]
        for option in parser[section]:
            data_type = config_model.get(section, option)
            if data_type in [STRING, IPADDR, SCREEN]:
                config_section[option] = parser.get(section, option)
            elif data_type == BOOLEAN:
                config_section[option] = parser.getboolean(section, option)
            elif data_type == INTEGER:
                config_section[option] = parser.getint(section, option)
            elif data_type == REAL:
                config_section[option] = parser.getfloat(section, option)
            elif data_type == ARRAY:
                raw_value = parser.get(section, option)
                filtered_values = filter(lambda x: (x or "") != "", [
                    value.strip() for value in raw_value.split(",")])

                config_section[option] = list(filtered_values)
            else:
                config_section[option] = parser.get(section, option)

    if config["Updates"]["Enabled"]:
        update_channel = config["Updates"]["Channel"]
        if update_channel not in ["Release", "Development"]:
            logger.error("Invalid update channel, please check the wiki.")

    return config


config = _load_config(_CONFIG_PATH)
