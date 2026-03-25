from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://postgres:postgres123@localhost/opportunity_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
class OpportunityRecord(Base):
    __tablename__ = "opportunities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    state = Column(String)
    naics_code = Column(Integer)
    opportunity_type = Column(String)
    dollar_amount = Column(Float)
    calendar_days = Column(Integer)
    days_until_response = Column(Integer)
    sow_match = Column(String)
    score = Column(Integer)
    result = Column(String)

def create_tables():
    Base.metadata.create_all(bind=engine)