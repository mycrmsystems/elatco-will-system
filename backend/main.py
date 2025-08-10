from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from datetime import datetime
from .database import Base

class Will(Base):
    __tablename__ = "wills"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Core client details
    client_name = Column(String(255))
    dob = Column(String(64))
    address = Column(Text)
    marital_status = Column(String(64), nullable=True)
    partner_name = Column(String(255), nullable=True)
    children = Column(Text, nullable=True)  # names/DOBs, one per line

    # Executors & Guardians
    executors = Column(Text, nullable=True)
    replacement_executors = Column(Text, nullable=True)
    guardians = Column(Text, nullable=True)

    # Gifts
    gifts_cash = Column(Text, nullable=True)         # £X to Person A … (one per line)
    gifts_specific = Column(Text, nullable=True)     # items / chattels to individuals
    charity_gifts = Column(Text, nullable=True)      # gifts to charities

    # Estate residue
    residuary_first_death = Column(Text, nullable=True)   # e.g. “to my spouse/partner absolutely”
    residuary_second_death = Column(Text, nullable=True)  # ultimate beneficiaries if both die / on survivor’s death

    # Preferences & Other Matters
    funeral_wishes = Column(Text, nullable=True)
    digital_assets = Column(Text, nullable=True)
    pet_wishes = Column(Text, nullable=True)
    business_interests = Column(Text, nullable=True)
    foreign_assets = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    # Trusts
    trust_type = Column(String(64), default="None")
    trustees = Column(Text, nullable=True)
    beneficiaries = Column(Text, nullable=True)
    age_of_access = Column(String(16), nullable=True)
    special_clauses = Column(Text, nullable=True)
    trust_text = Column(Text, nullable=True)

    # Mirroring
    is_mirrored_pair = Column(Boolean, default=False)     # true if created as a mirrored set
    mirror_group = Column(Integer, nullable=True)         # simple group id to link the pair (same number for both)

    # Output
    pdf_filename = Column(String(255), nullable=True)
