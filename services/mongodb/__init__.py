from data.config import Config
from data.map import Map
from data.user import User


from typing import ByteString, Dict, Optional


def find_config_by_key(key: str) -> Config:
    return Config.objects(key=key).first()


def find_map_by_key(key: str) -> Map:
    return Map.objects(key=key).first()


def find_user_by_key(key: str) -> User:
    return User.objects(key=key).first()


def set_config(key: str, tfm_menu: Dict) -> Config:
    config = find_config_by_key(key)
    if config:
        config.update(tfm_menu=tfm_menu)
    else:
        config = Config(key=key, tfm_menu=tfm_menu).save()
    return config


def set_map(key: str, data: ByteString) -> Map:
    _map = find_map_by_key(key)
    if _map:
        _map.update(data=data)
    else:
        _map = Map(key=key, data=data).save()
    return _map


def set_user(
    key: str,
    premium_level: Optional[str] = "SILVER",
    browser_access: Optional[bool] = False
) -> User:
    user = find_user_by_key(key)
    if user:
        user.update(premium_level=premium_level, browser_access=browser_access)
    else:
        user = User(
            key=key, premium_level=premium_level, browser_access=browser_access
        ).save()
    return
