from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

from functools import wraps
from sqlalchemy.orm import load_only
from typing import Any, ByteString, Dict, List, Optional

from data.config import Config
from data.map import Map
from data.soft import Soft
from data.user import User

import sqlalchemy
import sqlalchemy.orm
import os

from sqlalchemy.ext.mutable import MutableDict
MutableDict.associate_with(sqlalchemy.JSON)

class DBClient:
	def __init__(self, endpoint: str):
		engine = sqlalchemy.create_engine(endpoint)

		Session = sqlalchemy.orm.sessionmaker(bind=engine)
		self._session: sqlalchemy.orm.session.Session = Session()

		def commit(cls, func):
			@wraps(func)
			def wrapper(*args, **kwargs):
				result = func(*args, **kwargs)

				cls._session.commit()

				return result
			return wrapper

		for name in dir(self):
			obj = getattr(self, name)
			if callable(obj) and name.startswith("del_") or name.startswith("set_"):
				setattr(self, name, commit(self, obj))

	def commit(self):
		self._session.commit()

	def delete(self, obj: Any):
		self._session.delete(obj)

	def find_config_by_key(self, key: str) -> Config:
		return self._session.query(Config).get(key)

	def find_map_by_key(self, key: str, check_exists: Optional[bool] = False) -> bool | Map:
		if check_exists:
			return self._session.query(Map).options(load_only(Map.key)).get(key) is not None
		return self._session.query(Map).get(key)

	def find_soft_by_key(self, key: str) -> Soft:
		return self._session.query(Soft).get(key)

	def find_user_by_key(self, key: str) -> User:
		return self._session.query(User).get(key)

	def load_maps_keys(self) -> Any:
		return self._session.query(Map).options(load_only(Map.key)).all()

	def del_user(self, key: str) -> bool:
		user = self.find_user_by_key(key)
		if user:
			self._session.delete(user)
			return True
		return False

	def set_config(self, key: str, tfm_menu: Dict) -> Config:
		config = self.find_config_by_key(key)
		if config:
			config.tfm_menu = tfm_menu
		else:
			config = Config(key=key, tfm_menu=tfm_menu)
			self._session.add(config)

		return config

	def set_map(self, key: str, data: ByteString) -> Map:
		_map = self.find_map_by_key(key)
		if _map:
			_map.data = data
		else:
			_map = Map(key=key, data=data)
			self._session.add(_map)

		return _map

	def set_soft(self, key: str, maps: Optional[Dict] = {}) -> Soft:
		soft = self.find_soft_by_key(key)
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
			self._session.add(soft)

		return soft

	def set_user(self, key: str, level: Optional[str] = "GOLD_II", browser_access: Optional[bool] = True) -> User:
		level = level.upper()

		user = self.find_user_by_key(key)
		if user:
			user.level = level
			user.browser_access = browser_access
		else:
			user = User(key=key, level=level, browser_access=browser_access)
			self._session.add(user)

		return user

	def set_user_browser_token(self, key: str, token: Optional[str] = None) -> User:
		user = self.find_user_by_key(key)
		if user:
			user.update(browser_access=True, browser_access_token=token)
		return user

client = DBClient(os.getenv("MARIADB_ENDPOINT"))