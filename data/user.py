from data import Base

import sqlalchemy

class User(Base):
    __tablename__ = "users"

    key =  sqlalchemy.Column(sqlalchemy.String(16), primary_key=True)
    level = sqlalchemy.Column(sqlalchemy.String(10), default=str("GOLD_II"))

    browser_access = sqlalchemy.Column(sqlalchemy.Boolean, default=bool(True))
    browser_access_token = sqlalchemy.Column(sqlalchemy.String(40))
    key_hidden = sqlalchemy.Column(sqlalchemy.Boolean, default=bool(False))

    connection_limit = sqlalchemy.Column(sqlalchemy.Integer, default=(int(-1)))