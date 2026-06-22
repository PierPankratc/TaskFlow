from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import TaskSchema
from db.create_db import get_db_connect
from db.models import Projects, SubTasks, Tasks, Users
from .auth import security

router = APIRouter(prefix="/tasks", tags=["Задачи"])


def _get_owned_project(db: Session, uid: int, project_id: int) -> Projects:
    project = db.query(Projects).filter(
        Projects.id == project_id,
        Projects.user_id == uid,
    ).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/add", summary="Добавить задачу")
def add_task(
    task: TaskSchema,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)
    if not db.query(Users).filter(Users.id == uid).first():
        raise HTTPException(status_code=404, detail="User not found")

    if task.project_id is not None:
        _get_owned_project(db, uid, task.project_id)

    existing_task = db.query(Tasks).filter(
        Tasks.user_id == uid,
        Tasks.title == task.title,
    ).first()
    if existing_task:
        raise HTTPException(
            status_code=409,
            detail=f'Задача "{task.title}" уже существует',
        )

    new_task = Tasks(
        user_id=uid,
        project_id=task.project_id,
        title=task.title,
        deadline=task.deadline,
        status=task.status,
        priority=task.priority,
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "id": new_task.id,
        "title": new_task.title,
        "status": new_task.status,
        "priority": new_task.priority,
        "deadline": new_task.deadline,
        "project_id": new_task.project_id,
        "user_id": new_task.user_id,
    }


@router.delete("/del/{task_id}", summary="Удалить задачу")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
    confirm: bool = False,
):
    uid = int(payload.sub)
    if not db.query(Users).filter(Users.id == uid).first():
        raise HTTPException(status_code=404, detail="User not found")

    if not confirm:
        return {"confirm": "подтвердите удаление"}

    task = db.query(Tasks).filter(
        Tasks.id == task_id,
        Tasks.user_id == uid,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"del_task_id": task_id, "status": "deleted"}


@router.get("/get_all", summary="Вернуть все задачи")
def get_all_tasks(
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)
    return db.query(Tasks).filter(Tasks.user_id == uid).all()


@router.get("/task/{task_id}", summary="Получить задачу с подзадачами")
def get_task_with_subtasks(
    task_id: int,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)

    if not db.query(Users).filter(Users.id == uid).first():
        raise HTTPException(status_code=404, detail="User not found")

    task = db.query(Tasks).filter(
        Tasks.id == task_id,
        Tasks.user_id == uid,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    subtasks = db.query(SubTasks).filter(SubTasks.task_id == task_id).all()
    project = (
        db.query(Projects).filter(Projects.id == task.project_id).first()
        if task.project_id
        else None
    )

    return {
        "task": {
            "id": task.id,
            "title": task.title,
            "status": task.status,
            "priority": task.priority,
            "deadline": task.deadline,
            "created": task.created,
            "project_id": task.project_id,
        },
        "project": (
            {"id": project.id, "title": project.title} if project else None
        ),
        "subtasks": [
            {
                "id": subtask.id,
                "title": subtask.title,
                "status": subtask.status,
                "deadline": subtask.deadline,
                "priority": subtask.priority,
                "created": subtask.created,
            }
            for subtask in subtasks
        ],
        "summary": {"total_subtasks": len(subtasks)},
    }
