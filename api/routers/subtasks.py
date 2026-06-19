from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Response
from db.create_db import get_db_connect 
from api.schemas import UserSchema, SubTaskSchema
from sqlalchemy.orm import Session
from db.models import Users, Projects, Tasks, SubTasks
from .auth import security


router = APIRouter(prefix='/subtasks', tags=['Подзадачи'])

# ===== ЭНДПОИНТЫ =====




@router.post('/add', dependencies=[Depends(security.access_token_required)], summary='Добавить подзадачу')
def add_task(
    subtask: SubTaskSchema,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required)
):
    uid = int(payload.sub)
    
    # Проверяем пользователя
    user = db.query(Users).filter(Users.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    # Проверяем дубликат
    existing_task = db.query(SubTasks).filter(
        SubTasks.user_id == uid,
        SubTasks.title == subtask.title
    ).first()
    
    if existing_task:
        raise HTTPException(
            status_code=409,
            detail=f'Задача "{subtask.title}" уже существует'
        )
    
    new_task = SubTasks(
        user_id=uid,
        title=subtask.title,
        deadline=subtask.deadline,
        status=subtask.status,
        priority=subtask.priority
    )
    
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {
        'id': new_task.id,
        'title': new_task.title,
        'status': new_task.status,
        'priority': new_task.priority,
        'deadline': new_task.deadline,
        'user_id': new_task.user_id
    }



@router.delete('/del/{task_id}', dependencies=[Depends(security.access_token_required)], summary='Удалить задачу')
def del_task(task_id: int, db: Session = Depends(get_db_connect), payload: TokenPayload = Depends(security.access_token_required), confirm: bool = False):
    uid = int(payload.sub)
    user_ =  db.query(Users).filter(Users.id == uid).first()
    if not user_:
        raise HTTPException(status_code=404, detail='User not found')
        
    if confirm:
        del_task =  db.query(Tasks).filter(Tasks.id == task_id, Tasks.user_id == uid).delete()
        db.commit()
        return {
        'del_task_id': task_id,
        'status': 'deleted'
         }
    
    return {'confirm': 'подтвердите удаление'}


@router.get('get_all', summary='вернуть все задачи')
def get_all_projects(db: Session = Depends(get_db_connect), payload: TokenPayload = Depends(security.access_token_required)):
    uid = int(payload.sub)
    user_tasks = db.query(SubTasks).filter(SubTasks.user_id == uid).all()
    return user_tasks



