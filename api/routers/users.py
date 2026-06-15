from fastapi import APIRouter, Depends, HTTPException, Header, Response
from fastapi.security import OAuth2PasswordBearer
from db.create_db import get_db_connect 
from api.schemas import UserSchema, ProjectSchema, TaskSchema, SubTaskSchema
from sqlalchemy.orm import Session
from db.models import Users, Projects, Tasks, SubTasks
import jwt as PYjwt
from datetime import datetime, timedelta
from typing import Optional
from authx import AuthX, AuthXConfig, TokenPayload

router = APIRouter(prefix='/user', tags=['Пользователи'])


config = AuthXConfig()
config.JWT_SECRET_KEY = 'ggg'
config.JWT_ACCESS_COOKIE_NAME = 'access_token'
config.JWT_TOKEN_LOCATION = ['cookies']
config.JWT_COOKIE_CSRF_PROTECT = False

security = AuthX(config=config)

# ===== ЭНДПОИНТЫ =====

@router.post('/login')
def login(user: UserSchema, response: Response, db: Session = Depends(get_db_connect)):
    # Проверяем пользователя
    db_user = db.query(Users).filter(Users.name == user.name).first()
    
    if not db_user:
        # Создаём нового пользователя
        db_user = Users(name=user.name, password=user.password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
    elif db_user.password != user.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Создаём токен
    token = security.create_access_token(uid=str(db_user.id))
    response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
    return {'token': token}
    


@router.post('/add_project')
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















# @router.post('/add_task', dependencies=[Depends(security.access_token_required)])
# def add_task(
#     task: TaskSchema, 
#     db: Session = Depends(get_db_connect), 
    
# ):

#     new_task = Todo(
#         task=task.task,
#         status=task.status if task.status else False,
#         user_id=
#     )
#     db.add(new_task)
#     db.commit()
#     db.refresh(new_project)
#     return {
#         'id': new_project.id,
#         'task': new_project.title,
#         'status': new_project.status,
#         'deadline': new_project.deadline,
#         'user_id': new_project.user_id
#     }

# @router.get('{id}/pr')
# def ge_pr(uid: int, db: Session = Depends(get_db_connect)):
#     user_ =  db.query(Users).filter(id == Users.id).first()
#     if not user_:
#         raise HTTPException(status_code=404, detail='User not found')
    
#     pr = db.query(Projects).filter(Projects.user_id == uid).all()
#     lst = []
#     for p in pr:
#         lst.append({
#             'id': p.id,
#             'title': p.title
#         })
#     return {'prs': lst}


          


# @router.get('/my_tasks')
# def get_my_tasks(
#     db: Session = Depends(get_db_connect), 
#     current_user: Users = Depends(get_current_user_from_token)  # ← авторизация
# ):
#     tasks = db.query(Todo).filter(Todo.user_id == current_user.id).all()
    
#     task_list = []
#     for idx, task in enumerate(tasks, 1):
#         task_list.append({
#             'id': task.id,
#             'task': task.task,
#             'status': task.status
#         })
    
#     return {
#         'user_id': current_user.id,
#         'user_name': current_user.name,
#         'tasks': task_list
#     }


# @router.put('/update_task/{task_id}')
# def update_task(
#     task_id: int, 
#     new_task: str, 
#     db: Session = Depends(get_db_connect),
#     current_user: Users = Depends(get_current_user_from_token)  # ← авторизация
# ):
#     """Обновить задачу (только владелец задачи)"""
#     task = db.query(Todo).filter(Todo.id == task_id).first()
    
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     # Проверяем, что задача принадлежит текущему пользователю
#     if task.user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="You don't have permission to update this task")
    
#     task.task = new_task
#     db.commit()
#     db.refresh(task)
    
#     return {
#         'id': task.id, 
#         'task': task.task, 
#         'status': task.status
#     }


# @router.delete('/delete_task/{task_id}')
# def delete_task(
#     task_id: int, 
#     confirm: bool = False, 
#     db: Session = Depends(get_db_connect),
#     current_user: Users = Depends(get_current_user_from_token) 
# ):

#     task = db.query(Todo).filter(Todo.id == task_id).first()
    
#     if not task:
#         raise HTTPException(status_code=404, detail="Task not found")
    
#     # Проверяем, что задача принадлежит текущему пользователю
#     if task.user_id != current_user.id:
#         raise HTTPException(status_code=403, detail="You don't have permission to delete this task")
    
#     if not confirm:
#         return {
#             'warning': 'Вы уверены, что хотите удалить эту задачу?',
#             'task': task.task,
#             'action': f'DELETE /user/delete_task/{task_id}?confirm=true'
#         }
    
#     db.delete(task)
#     db.commit()
#     return {'message': f'Task {task_id} deleted', 'task': task.task}


# @router.get('/me')
# def get_me(
#     current_user: Users = Depends(get_current_user_from_token)
# ):
    
#     return {
#         'id': current_user.id,
#         'name': current_user.name
#     }