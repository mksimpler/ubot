import sys
from os import path
from glob import glob
from importlib import util
from pathlib import Path

import re
import types

from ubot import logger
from ubot.config import config
from ubot.sprite import Sprite

from ubot.settings import DEVELOPMENT_MODE_ACTIVE


def load_module(module_name, module_path):
    """
    Load module from given path

    Args:
        module_name: string
        module_path: string

    Return:
        module
    """
    module_filepath = module_path
    (_, ext) = path.splitext(module_path)

    if ext != ".py":
        module_filepath = path.join(module_path, "__init__.py")

    spec = util.spec_from_file_location(module_name, module_filepath)
    module = util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class PackageError(BaseException):
    pass


class Package:

    def __init__(self, package_name, package_path=None):
        self.name = package_name

        self.pkg_loc = f"packages/{self.name}" if package_path is None else package_path
        self._append_sys_path()

        self.sprites = self._discorver_sprites()
        self.pkg_module = self._load_package_module(package_path)

        self.package = types.SimpleNamespace(
            logger=logger,
            config=config
        )

    def execute(self):
        if callable(self.pkg_module.init):
            try:
                self.pkg_module.init(self.package)
            except BaseException as ex:
                if DEVELOPMENT_MODE_ACTIVE:
                    raise ex
                else:
                    logger.error(str(ex))

        pkg_toolkit = _PackageToolkit(self, self.package.config)

        if callable(self.pkg_module.start):
            try:
                self.pkg_module.start(self.package, pkg_toolkit.toolkit)
            except BaseException as ex:
                if DEVELOPMENT_MODE_ACTIVE:
                    raise ex
                else:
                    logger.error(str(ex))

    def _discorver_sprites(self):
        sprites = dict()

        sprites_path = path.join(self.pkg_loc, "sprites")
        sprites_path_parts = re.split(r"[\\/]", sprites_path)

        for sprite_path in Path(sprites_path).rglob("*.png"):
            sprite_name = "/".join([p for p in sprite_path.parts if p not in sprites_path_parts]).lower().replace(".png", "")
            sprite = Sprite.from_path(str(sprite_path), name=sprite_name)

            if sprite_name not in sprites:
                sprites[sprite_name] = sprite
            else:
                sprites[sprite_name].append_image_data(sprite_image_data)

        return sprites

    def _load_package_module(self, package_path):
        module_name = 'packages.{}'.format(self.name)
        module_path = package_path if package_path is not None else 'packages/{}'.format(self.name)

        if len(glob(module_path + '/__init__.py')) == 0:
            raise PackageError("Invalid packages")

        return load_module(module_name, module_path)

    def _append_sys_path(self):
        sys.path.append(path.realpath(self.pkg_loc))


class _PackageToolkit:

    def __init__(self, package, config):
        self.package = package
        self.config = config

        self.toolkit = types.SimpleNamespace(
            bot_maker=self.gen_bot_maker(),
            sprite_locator=self.gen_sprite_locator(),
            ocr=self.gen_ocr(),
            coords=self.gen_coords()
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


def load_package(package_name, package_path=None):
    """
    Load package from given name

    Args:
        package_name: string

    Return:
        module
    """
    return Package(package_name, package_path=package_path)
