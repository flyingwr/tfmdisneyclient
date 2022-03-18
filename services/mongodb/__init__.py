from data.blacklist import Blacklist
from data.config import Config
from data.map import Map
from data.soft import Soft
from data.user import User


from typing import ByteString, Dict, Optional, Union


import infrastructure


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


def del_blacklist(addr: str):
    blacklist = Blacklist.objects(addr=addr).first()
    if blacklist:
        blacklist.delete()

        infrastructure.blacklisted_ips.remove(addr)


def set_blacklist(addr: str) -> Blacklist:
    blacklist = Blacklist.objects(addr=addr).first()
    if not blacklist:
        blacklist = Blacklist(addr=addr).save()

        infrastructure.blacklisted_ips.append(addr)
        
    return blacklist
    

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
    premium_level: Optional[str] = "GOLD_II",
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