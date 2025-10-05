from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1 import api_router
from app.core.database import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    sessionmanager.init_db()
    yield
    await sessionmanager.close()


app = FastAPI(
    title="Finance Tracker API",
    description="API for finance tracker",
    version="1.0",
    docs_url="/",

    lifespan=lifespan,
)

app.include_router(api_router)
