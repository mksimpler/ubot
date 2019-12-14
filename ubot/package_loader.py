import sys
from os import path
from glob import glob
from importlib import util
from pathlib import Path

import re

from ubot.sprite import Sprite


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

    def start(self, *args, **kwargs):
        self.pkg_module.start(*args, **kwargs)

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


def load_package(package_name, package_path=None):
    """
    Load package from given name

    Args:
        package_name: string

    Return:
        module
    """
    return Package(package_name, package_path=package_path)
