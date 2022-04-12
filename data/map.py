from sqlalchemy.sql import func

from data import Base

import sqlalchemy

class Map(Base):
    __tablename__ = "map"

    key =  sqlalchemy.Column(sqlalchemy.String(16), primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.LargeBinary)

    modified = sqlalchemy.Column(sqlalchemy.TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())