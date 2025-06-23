from fastapi import FastAPI
from neomediapi.api.v1.routes import users

app = FastAPI()

app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
