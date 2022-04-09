from data import Base

import sqlalchemy

class Config(Base):
    __tablename__ = "config"
    
    key = sqlalchemy.Column(sqlalchemy.String(16), primary_key=True)
    tfm_menu = sqlalchemy.Column(sqlalchemy.JSON)