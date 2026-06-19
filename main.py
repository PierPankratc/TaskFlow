from fastapi import FastAPI
import uvicorn 
from api.routers import projects, auth, tasks, subtasks

app = FastAPI()

app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(subtasks.router)

if __name__ == '__main__':
    uvicorn.run(app='main:app', reload = True)
