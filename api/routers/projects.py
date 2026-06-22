from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import ProjectSchema
from db.create_db import get_db_connect
from db.models import Projects, SubTasks, Tasks, Users
from .auth import security

router = APIRouter(prefix="/project", tags=["Проекты"])


@router.post("/add", summary="Добавить проект")
def add_project(
    project: ProjectSchema,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)
    user = db.query(Users).filter(Users.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = db.query(Projects).filter(
        Projects.user_id == uid,
        Projects.title == project.title,
    ).first()
    if existing:
        raise HTTPException(
            status_code=409,
            detail=f'Проект "{project.title}" уже существует',
        )

    new_project = Projects(
        user_id=uid,
        title=project.title,
        created=project.created,
        deadline=project.deadline,
        status=project.status,
        priority=project.priority,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        "id": new_project.id,
        "title": new_project.title,
        "status": new_project.status,
        "deadline": new_project.deadline,
        "user_id": new_project.user_id,
    }


@router.delete("/del/{project_id}", summary="Удалить проект")
def delete_project(
    project_id: int,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
    confirm: bool = False,
):
    uid = int(payload.sub)
    if not db.query(Users).filter(Users.id == uid).first():
        raise HTTPException(status_code=404, detail="User not found")

    if not confirm:
        return {"confirm": "подтвердите удаление"}

    project = db.query(Projects).filter(
        Projects.id == project_id,
        Projects.user_id == uid,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()
    return {"del_project_id": project_id, "status": "deleted"}


@router.get("/get_all", summary="Вернуть все проекты")
def get_all_projects(
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)
    return db.query(Projects).filter(Projects.user_id == uid).all()


@router.get("/three/{project_id}", summary="Вернуть проект, задачи и подзадачи")
def get_project_with_tasks(
    project_id: int,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)

    if not db.query(Users).filter(Users.id == uid).first():
        raise HTTPException(status_code=404, detail="User not found")

    project = db.query(Projects).filter(
        Projects.id == project_id,
        Projects.user_id == uid,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = db.query(Tasks).filter(
        Tasks.project_id == project_id,
        Tasks.user_id == uid,
    ).all()

    task_ids = [task.id for task in tasks]
    subtasks = (
        db.query(SubTasks).filter(SubTasks.task_id.in_(task_ids)).all()
        if task_ids
        else []
    )

    return {
        "project": {
            "id": project.id,
            "title": project.title,
            "status": project.status,
            "priority": project.priority,
            "deadline": project.deadline,
            "created": project.created,
        },
        "tasks": [
            {
                "id": task.id,
                "title": task.title,
                "status": task.status,
                "priority": task.priority,
                "deadline": task.deadline,
            }
            for task in tasks
        ],
        "subtasks": [
            {
                "id": subtask.id,
                "title": subtask.title,
                "status": subtask.status,
                "task_id": subtask.task_id,
            }
            for subtask in subtasks
        ],
        "summary": {
            "total_tasks": len(tasks),
            "total_subtasks": len(subtasks),
        },
    }
