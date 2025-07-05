from fastapi import FastAPI
from neomediapi.api.v1.routes import users
from neomediapi.api.v1.routes import session
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(session.router, prefix="/api/v1/session", tags=["session"])


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
