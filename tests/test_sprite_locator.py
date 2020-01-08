import pytest

import cv2

from ubot.image import Frame, Sprite
from ubot.sprite_locator import SpriteLocator


def test_locate_should_find_atleast_one_result():
    locator = SpriteLocator()
    frame = Frame(cv2.imread("./tests/frames/combat_01.png"))

    sprite = Sprite.frompath("./tests/sprites/enemy_s.png", "enemy_s")
    regions = locator.locate(sprite, frame, m_scale=0.75, threshold=0.84376, return_list=True)
    assert len(regions) >= 1

    sprite = Sprite.frompath("./tests/sprites/enemy_m.png", "enemy_m")
    regions = locator.locate(sprite, frame, m_scale=0.75, threshold=0.84376, return_list=True)
    assert len(regions) >= 1

    sprite = Sprite.frompath("./tests/sprites/enemy_l.png", "enemy_l")
    regions = locator.locate(sprite, frame, m_scale=0.6, threshold=0.7, return_list=True)
    assert len(regions) >= 1
