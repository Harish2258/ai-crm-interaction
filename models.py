from sqlalchemy import Column, Integer, String
from app.database import Base

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    hcp_name = Column(String)
    drug = Column(String)
    notes = Column(String)
    sentiment = Column(String)