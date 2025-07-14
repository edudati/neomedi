import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from neomediapi.infra.db.models.user_model import Base
from neomediapi.infra.db.models.address_model import Address
from neomediapi.infra.db.models.company_model import Company
from neomediapi.infra.db.models.medical_record_model import MedicalRecord
from neomediapi.infra.db.models.appointment_model import Appointment
from neomediapi.infra.db.models.professional_availability_model import ProfessionalAvailability
from neomediapi.infra.db.models.facility_model import Facility
from neomediapi.infra.db.models.facility_schedule_model import FacilitySchedule
from neomediapi.infra.db.models.recurring_reservation_model import RecurringReservation

# Load .env if not already loaded
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_all_tables():
    Base.metadata.create_all(bind=engine)
