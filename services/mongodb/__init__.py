from data.config import Config
from data.map import Map
from data.soft import Soft
from data.user import User
from utils import cryptjson


from typing import ByteString, Dict, Optional, Union


import aiofiles
import re

map_pattern = re.compile(b"(.*?):(.*)")


def find_config_by_key(key: str) -> Config:
    return Config.objects(key=key).first()


def find_map_by_key(key: str, return_count: Optional[bool] = False) -> Union[int, Map]:
    if return_count:
        return Map.objects(key=key).only("key").count()
    return Map.objects(key=key).first()


def find_soft_by_key(key: str) -> Soft:
    return Soft.objects(key=key).first()


def find_user_by_key(key: str) -> User:
    return User.objects(key=key).first()


def set_config(key: str, tfm_menu: Dict) -> Config:
    config = find_config_by_key(key)
    if config:
        config.update(tfm_menu=tfm_menu)
    else:
        config = Config(key=key, tfm_menu=tfm_menu).save()

    return config


def set_map(key: str, data: Optional[Dict] = {}) -> Map:
    _map = find_map_by_key(key)
    if _map:
        _map.data = maps
    else
        _map = Map(key=key, data=maps)
    return _map.save()


async def set_map_from_file(file: str, key: str) -> Map:
    maps = {}

    async with aiofiles.open(file, "rb") as f:
        content = await f.read()
        data = cryptjson.text_decode(content)
        for s in data.split(b"#"):
            search = map_pattern.search(s)
            if search:
                maps[search.group(1)] = search.group(2)

    set_map(key, maps)


def set_soft(key: str, maps: Optional[Dict] = {}) -> Soft:
    soft = find_soft_by_key(key)
    if soft:
        if not maps:
            soft.maps = maps
        else:
            for code, info in maps.items():
                if bool(info):
                    soft.maps[code] = info
                else:
                    if code in soft.maps:
                        del soft.maps[code]
    else:
        soft = Soft(key=key, maps=maps)

    return soft.save()


def set_user(
    key: str,
    premium_level: Optional[str] = "SILVER",
    browser_access: Optional[bool] = True,
    skip_check: Optional[bool] = False
) -> User:
    user = None if skip_check else find_user_by_key(key)
    if user:
        user.update(premium_level=premium_level, browser_access=browser_access)
    else:
        user = User(
            key=key, premium_level=premium_level, browser_access=browser_access
        ).save()

    return user


def set_user_browser_token(key: str, token: Optional[str] = None) -> User:
    user = find_user_by_key(key)
    if user:
        user.update(browser_access=True, browser_access_token=token)
    else:
        set_user(key, skip_check=True)

    return user
