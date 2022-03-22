from data import Base

import sqlalchemy

class Soft(Base):
    __tablename__ = "soft"

    key =  sqlalchemy.Column(sqlalchemy.String(16), primary_key=True)
    maps = sqlalchemy.Column(sqlalchemy.JSON)