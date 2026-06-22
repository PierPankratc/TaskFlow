from contextlib import asynccontextmanager

import uvicorn
from authx.exceptions import AuthXException
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from api.routers import auth, projects, subtasks, tasks
from db.create_db import create_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    create_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(AuthXException)
async def authx_exception_handler(_: Request, exc: AuthXException):
    return JSONResponse(status_code=401, content={"detail": str(exc)})


app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(subtasks.router)


if __name__ == "__main__":
    uvicorn.run(app="main:app", reload=True)
