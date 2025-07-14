from fastapi import FastAPI
from neomediapi.api.v1.routes import users
from neomediapi.api.v1.routes import session
from neomediapi.api.v1.routes import addresses
from neomediapi.api.v1.routes import companies
from neomediapi.api.v1.routes import company_users
from neomediapi.api.v1.routes import user_management
from neomediapi.api.v1.routes import medical_records
from neomediapi.api.v1.routes import appointments
from neomediapi.api.v1.routes import facilities
from neomediapi.api.v1.routes import recurring_reservations
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(session.router, prefix="/api/v1/session", tags=["session"])
app.include_router(addresses.router, prefix="/api/v1/addresses", tags=["addresses"])
app.include_router(companies.router, prefix="/api/v1", tags=["companies"])
app.include_router(company_users.router, prefix="/api/v1", tags=["company-users"])
app.include_router(user_management.router, prefix="/api/v1", tags=["user-management"])
app.include_router(medical_records.router, prefix="/api/v1/medical-records", tags=["medical-records"])
app.include_router(appointments.router, prefix="/api/v1", tags=["appointments"])
app.include_router(facilities.router, prefix="/api/v1", tags=["facilities"])
app.include_router(recurring_reservations.router, prefix="/api/v1", tags=["recurring-reservations"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
