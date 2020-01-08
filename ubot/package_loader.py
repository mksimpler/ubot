import sys
from os import path
from glob import glob
from importlib import util
from pathlib import Path

import re
import types

from ubot import logger
from ubot.config import config
from ubot.image import Sprite

from ubot.settings import DEVELOPMENT_MODE_ACTIVE


class PackageError(BaseException):
    pass


class Package:

    def __init__(self, package_name, package_path, module):
        self.name = package_name
        self.package_path = package_path
        self.package_module = module

        self.sprites = self._discorver_sprites()

        self.logger = logger

        self.config = config

    def execute(self):
        if callable(self.package_module.init):
            try:
                self.package_module.init(self)
            except BaseException as ex:
                if DEVELOPMENT_MODE_ACTIVE:
                    raise ex
                else:
                    logger.error(str(ex))

        package_toolkit = PackageToolkit(self, self.config)

        if callable(self.package_module.start):
            try:
                self.package_module.start(self, package_toolkit.toolkit)
            except BaseException as ex:
                if DEVELOPMENT_MODE_ACTIVE:
                    raise ex
                else:
                    logger.error(str(ex))

    def _discorver_sprites(self):
        sprites = dict()

        sprites_path = Path(path.join(self.package_path, "sprites"))

        for sprite_path in sprites_path.rglob("*.png"):
            sprite_name = "/".join([p for p in sprite_path.parts if p not in sprites_path.parts]).lower().replace(".png", "")
            sprite = Sprite.frompath(str(sprite_path), name=sprite_name)

            if sprite_name not in sprites:
                sprites[sprite_name] = sprite
            else:
                sprites[sprite_name].append_image_data(sprite_image_data)

        return sprites


class PackageToolkit:

    def __init__(self, package, config):
        self.package = package
        self.config = config

        self.toolkit = types.SimpleNamespace(
            bot_maker=self.gen_bot_maker(),
            sprite_locator=self.gen_sprite_locator(),
            ocr=self.gen_ocr(),
            coords=self.gen_coords(),
            utils=self.gen_utils()
        )

    def gen_bot_maker(self):

        def _make_bot(bot_type, **kwargs):
            from ubot.bots import make
            return make(bot_type, self.config, self.package, **kwargs)

        return types.SimpleNamespace(
            make=_make_bot
        )

    def gen_sprite_locator(self):
        from ubot.sprite_locator import SpriteLocator
        return SpriteLocator()

    def gen_ocr(self):
        from ubot import ocr
        return ocr

    def gen_coords(self):
        from ubot.coordinates import as_coordinate, filter_coord, filter_similar_coords
        return types.SimpleNamespace(
            as_coordinate=as_coordinate,
            filter_coord=filter_coord,
            filter_similar_coords=filter_similar_coords
        )

    def gen_utils(self):
        from ubot.utilities import extract_region_from_image, draw_retangle
        return types.SimpleNamespace(
            extract_region_from_image=extract_region_from_image,
            draw_retangle=draw_retangle
        )


def load_module(module_name, module_path):
    """
    Load module from given path

    Args:
        module_name: string
        module_path: string

    Return:
        module
    """
    if Path(module_path).suffix != ".py":

        module_tmp_path = path.join(module_path, "__init__.py")

        if Path(module_tmp_path).is_file():
            module_path = str(module_tmp_path.resolve())

        else:
            raise PackageError(f"Cannot import module '{module_path}'")

    spec = util.spec_from_file_location(module_name, module_path)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def load_package(package_path):
    """
    Load package from given name

    Args:
        package_name: string

    Return:
        module
    """

    package_entries = [
        Path(package_path),
        Path(path.join(package_path, "__main__.py")),
        Path(f"./packages/{package_path}/__main__.py")
    ]

    package_name = None
    package_path = None
    package_filepath = None

    for package_entry in package_entries:
        if package_entry.is_file() and package_entry.name == "__main__.py":

            package_entry = package_entry.resolve()

            package_name = package_entry.parts[-2]
            package_path = path.join(*package_entry.parts[:-1])
            package_filepath = str(package_entry)

            break
    else:
        raise PackageError(f"Package '{package_path}' not found")

    if package_path not in sys.path:
        sys.path.append(package_path)

    module = load_module(package_name, package_filepath)

    return Package(package_name, package_path, module)
