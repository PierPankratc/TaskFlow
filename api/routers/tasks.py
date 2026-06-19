from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Response
from db.create_db import get_db_connect 
from api.schemas import UserSchema, ProjectSchema, TaskSchema, SubTaskSchema
from sqlalchemy.orm import Session
from db.models import Users, Projects, Tasks, SubTasks
from .auth import security


router = APIRouter(prefix='/tasks', tags=['Задачи'])

# ===== ЭНДПОИНТЫ =====




@router.post('/add', dependencies=[Depends(security.access_token_required)], summary='Добавить задачу')
def add_task(
    task: TaskSchema,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required)
):
    uid = int(payload.sub)
    
    # Проверяем пользователя
    user = db.query(Users).filter(Users.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    # Проверяем дубликат
    existing_task = db.query(Tasks).filter(
        Tasks.user_id == uid,
        Tasks.title == task.title
    ).first()
    
    if existing_task:
        raise HTTPException(
            status_code=409,
            detail=f'Задача "{task.title}" уже существует'
        )
    
    new_task = Tasks(
        user_id=uid,
        title=task.title,
        deadline=task.deadline,
        status=task.status,
        priority=task.priority
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
    user_tasks = db.query(Tasks).filter(Tasks.user_id == uid).all()
    return user_tasks


@router.get('/task/{task_id}', summary='Получить задачу с подзадачами')
def get_task_with_subtasks(
    task_id: int,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required)
):
    uid = int(payload.sub)
    
    # Проверяем пользователя
    user = db.query(Users).filter(Users.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    # 1. Получаем задачу
    task = db.query(Tasks).filter(
        Tasks.id == task_id,
        Tasks.user_id == uid
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail='Task not found')
    
    # 2. Получаем все подзадачи этой задачи
    subtasks = db.query(SubTasks).filter(SubTasks.task_id == task_id).all()
    
    # 3. Получаем проект, к которому относится задача (опционально)
    project = db.query(Projects).filter(Projects.id == task.project_id).first()
    
    # 4. Формируем ответ
    return {
        'task': {
            'id': task.id,
            'title': task.title,
            'status': task.status,
            'priority': task.priority,
            'deadline': task.deadline,
            'created': task.created,
            'project_id': task.project_id
        },
        'project': {
            'id': project.id,
            'title': project.title
        } if project else None,
        'subtasks': [
            {
                'id': subtask.id,
                'title': subtask.title,
                'status': subtask.status,
                'deadline': subtask.deadline,
                'priority': subtask.priority,
                'created': subtask.created
            }
            for subtask in subtasks
        ],
        'summary': {
            'total_subtasks': len(subtasks)
        }
    }