from data import Base

import sqlalchemy

class Soft(Base):
    __tablename__ = "soft"

    key =  sqlalchemy.Column(sqlalchemy.String(16), primary_key=True)
    data = sqlalchemy.Column(sqlalchemy.LargeBinary(8388608))