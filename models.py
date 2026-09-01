from database import Base
from sqlalchemy import Boolean, Column, Integer, String

class Subscribers(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    city = Column(String)
    is_active = Column(Boolean, default=True)
    chat_id = Column(Integer, unique=True)