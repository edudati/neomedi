from fastapi import FastAPI
from neomediapi.api.v1.routes import users

app = FastAPI()

# Inclua as rotas dos endpoints
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
