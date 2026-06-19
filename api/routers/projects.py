from authx import TokenPayload
from fastapi import APIRouter, Depends, HTTPException, Response
from db.create_db import get_db_connect 
from api.schemas import ProjectSchema
from sqlalchemy.orm import Session
from db.models import Users, Projects, Tasks, SubTasks
from .auth import security


router = APIRouter(prefix='/project', tags=['Проекты'])

# ===== ЭНДПОИНТЫ =====




@router.post('/add', dependencies=[Depends(security.access_token_required)], summary='Добавить проект')
def add_project(project: ProjectSchema, db: Session = Depends(get_db_connect), payload: TokenPayload = Depends(security.access_token_required)):
    uid = int(payload.sub)
    user_ =  db.query(Users).filter(Users.id == uid).first()
    
    if not user_:
        raise HTTPException(status_code=404, detail='User not found')
        
    project_ =  db.query(Projects).filter(Projects.user_id == uid, Projects.title == project.title).first()
    if project_:
        return {
            'Error': 'вы уже записали данный проект',
            'title': project.title
            }
        
            
    new_project = Projects(
        user_id = uid,
        title = project.title,
        deadline = project.deadline,
        status = project.status,
        priority = project.priority
        )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return {
        'id': new_project.id,
        'task': new_project.title,
        'status': new_project.status,
        'deadline': new_project.deadline,
        'user_id': new_project.user_id
    }

@router.delete('/del/{project_id}', dependencies=[Depends(security.access_token_required)], summary='Удалить проект')
def upt_project(project_id: int, db: Session = Depends(get_db_connect), payload: TokenPayload = Depends(security.access_token_required), confirm: bool = False):
    uid = int(payload.sub)
    user_ =  db.query(Users).filter(Users.id == uid).first()
    if not user_:
        raise HTTPException(status_code=404, detail='User not found')
        
    if confirm:
        del_project =  db.query(Projects).filter(Projects.id == project_id, Projects.user_id == uid).delete()
        db.commit()
        return {
        'del_project_id': project_id,
        'status': 'deleted'
         }
    
    return {'confirm': 'подтвердите удаление'}

@router.get('get_all', summary='вернуть все проекты проекты')
def get_all_projects(db: Session = Depends(get_db_connect), payload: TokenPayload = Depends(security.access_token_required)):
    uid = int(payload.sub)
    user_projects = db.query(Projects).filter(Projects.user_id == uid).all()
    return user_projects


@router.get('/three/{project_id}', summary='вернуть проект, задачи и подзадачи')
def get_project_with_tasks(
    project_id: int,
    db: Session = Depends(get_db_connect),
    payload: TokenPayload = Depends(security.access_token_required)
):
    uid = int(payload.sub)
    
    # Проверяем пользователя
    user = db.query(Users).filter(Users.id == uid).first()
    if not user:
        raise HTTPException(status_code=404, detail='User not found')
    
    # 1. Получаем проект
    project = db.query(Projects).filter(
        Projects.id == project_id,
        Projects.user_id == uid
    ).first()
    
    if not project:
        raise HTTPException(status_code=404, detail='Project not found')
    
    # 2. Получаем все задачи проекта
    tasks = db.query(Tasks).filter(Tasks.project_id == project_id).all()
    
    # 3. Получаем все подзадачи для каждой задачи
    subtasks = []
    for task in tasks:
        subtask_list = db.query(SubTasks).filter(SubTasks.task_id == task.id).all()
        subtasks.extend(subtask_list)  # ← extend, а не append
    
    # 4. Формируем ответ
    return {
        'project': {
            'id': project.id,
            'title': project.title,
            'status': project.status,
            'priority': project.priority,
            'deadline': project.deadline,
            'created': project.created
        },
        'tasks': [
            {
                'id': task.id,
                'title': task.title,
                'status': task.status,
                'priority': task.priority,
                'deadline': task.deadline
            }
            for task in tasks
        ],
        'subtasks': [
            {
                'id': subtask.id,
                'title': subtask.title,
                'status': subtask.status,
                'task_id': subtask.task_id
            }
            for subtask in subtasks
        ],
        'summary': {
            'total_tasks': len(tasks),
            'total_subtasks': len(subtasks)
        }
    }




