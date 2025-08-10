from sqlalchemy import Column, Integer, String, DateTime, Text
from datetime import datetime
from .database import Base

class Will(Base):
    __tablename__ = "wills"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Client details
    client_name = Column(String(255))
    dob = Column(String(64))
    address = Column(Text)

    # Will content
    executors = Column(Text)
    guardians = Column(Text)
    gifts = Column(Text)
    residuary = Column(Text)

    # Trust
    trust_type = Column(String(64), default="None")
    trust_text = Column(Text)

    # Output
    pdf_filename = Column(String(255), nullable=True)
