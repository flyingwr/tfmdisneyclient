from data import Base

import sqlalchemy

class Map(Base):
    __tablename__ = "map"

    key =  sqlalchemy.Column(sqlalchemy.String(16), primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.LargeBinary)