from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.schemas import SubTaskSchema
from db.create_db import get_db_connect
from db.models import SubTasks, Tasks, Users
from .auth import security

router = APIRouter(prefix="/subtasks", tags=["Подзадачи"])


def _get_owned_task(db: Session, uid: int, task_id: int) -> Tasks:
    task = db.query(Tasks).filter(
        Tasks.id == task_id,
        Tasks.user_id == uid,
    ).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.post("/add", summary="Добавить подзадачу")
def add_subtask(
    subtask: SubTaskSchema,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)
    if not db.query(Users).filter(Users.id == uid).first():
        raise HTTPException(status_code=404, detail="User not found")

    if subtask.task_id is not None:
        _get_owned_task(db, uid, subtask.task_id)

    existing_subtask = db.query(SubTasks).filter(
        SubTasks.user_id == uid,
        SubTasks.title == subtask.title,
    ).first()
    if existing_subtask:
        raise HTTPException(
            status_code=409,
            detail=f'Подзадача "{subtask.title}" уже существует',
        )

    new_subtask = SubTasks(
        user_id=uid,
        task_id=subtask.task_id,
        title=subtask.title,
        deadline=subtask.deadline,
        status=subtask.status,
        priority=subtask.priority,
    )

    db.add(new_subtask)
    db.commit()
    db.refresh(new_subtask)

    return {
        "id": new_subtask.id,
        "title": new_subtask.title,
        "status": new_subtask.status,
        "priority": new_subtask.priority,
        "deadline": new_subtask.deadline,
        "task_id": new_subtask.task_id,
        "user_id": new_subtask.user_id,
    }


@router.delete("/del/{subtask_id}", summary="Удалить подзадачу")
def delete_subtask(
    subtask_id: int,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
    confirm: bool = False,
):
    uid = int(payload.sub)
    if not db.query(Users).filter(Users.id == uid).first():
        raise HTTPException(status_code=404, detail="User not found")

    if not confirm:
        return {"confirm": "подтвердите удаление"}

    subtask = db.query(SubTasks).filter(
        SubTasks.id == subtask_id,
        SubTasks.user_id == uid,
    ).first()
    if not subtask:
        raise HTTPException(status_code=404, detail="Subtask not found")

    db.delete(subtask)
    db.commit()
    return {"del_subtask_id": subtask_id, "status": "deleted"}


@router.get("/get_all", summary="Вернуть все подзадачи")
def get_all_subtasks(
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required),
):
    uid = int(payload.sub)
    return db.query(SubTasks).filter(SubTasks.user_id == uid).all()
