from fastapi import APIRouter, Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from db.create_db import get_db_connect 
from api.schemas import UserSchema, TaskSchema
from sqlalchemy.orm import Session
from db.models import Users, Todo
import jwt as PYjwt
from datetime import datetime, timedelta
from typing import Optional

SECRET_KEY = "secret"
ALGORITHM = "HS256"

router = APIRouter(prefix='/user', tags=['Пользователи'])

# OAuth2 схема (для Swagger)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user/login", auto_error=False)

# ===== ФУНКЦИИ АВТОРИЗАЦИИ =====
def get_current_user_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_connect)
):

    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        payload = PYjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except PYjwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(Users).filter(Users.id == int(user_id)).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_user_id_from_token(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db_connect)
):

    user = get_current_user_from_token(token, db)
    return user.id


# Альтернативный способ получения токена из заголовка (без OAuth2)
def get_token_from_header(authorization: str = Header(...)):
   
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    return authorization.replace("Bearer ", "")


# ===== ЭНДПОИНТЫ =====

@router.post('/login')
def login(user: UserSchema, db: Session = Depends(get_db_connect)):
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
    token = PYjwt.encode(
        {
            'sub': str(db_user.id), 
            'exp': datetime.utcnow() + timedelta(hours=1)
        },
        SECRET_KEY, 
        algorithm=ALGORITHM
    )
    
    return {
        'access_token': token,
        'token_type': 'bearer',
        'user_id': db_user.id
    }


@router.post('/add_task')
def add_task(
    task: TaskSchema, 
    db: Session = Depends(get_db_connect), 
    current_user: Users = Depends(get_current_user_from_token) 
):

    new_task = Todo(
        task=task.task,
        status=task.status if task.status else False,
        user_id=current_user.id
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    return {
        'id': new_task.id,
        'task': new_task.task,
        'status': new_task.status,
        'user_id': current_user.id
    }


@router.get('/my_tasks')
def get_my_tasks(
    db: Session = Depends(get_db_connect), 
    current_user: Users = Depends(get_current_user_from_token)  # ← авторизация
):
    tasks = db.query(Todo).filter(Todo.user_id == current_user.id).all()
    
    task_list = []
    for idx, task in enumerate(tasks, 1):
        task_list.append({
            'id': task.id,
            'task': task.task,
            'status': task.status
        })
    
    return {
        'user_id': current_user.id,
        'user_name': current_user.name,
        'tasks': task_list
    }


@router.put('/update_task/{task_id}')
def update_task(
    task_id: int, 
    new_task: str, 
    db: Session = Depends(get_db_connect),
    current_user: Users = Depends(get_current_user_from_token)  # ← авторизация
):
    """Обновить задачу (только владелец задачи)"""
    task = db.query(Todo).filter(Todo.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверяем, что задача принадлежит текущему пользователю
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to update this task")
    
    task.task = new_task
    db.commit()
    db.refresh(task)
    
    return {
        'id': task.id, 
        'task': task.task, 
        'status': task.status
    }


@router.delete('/delete_task/{task_id}')
def delete_task(
    task_id: int, 
    confirm: bool = False, 
    db: Session = Depends(get_db_connect),
    current_user: Users = Depends(get_current_user_from_token) 
):

    task = db.query(Todo).filter(Todo.id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Проверяем, что задача принадлежит текущему пользователю
    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this task")
    
    if not confirm:
        return {
            'warning': 'Вы уверены, что хотите удалить эту задачу?',
            'task': task.task,
            'action': f'DELETE /user/delete_task/{task_id}?confirm=true'
        }
    
    db.delete(task)
    db.commit()
    return {'message': f'Task {task_id} deleted', 'task': task.task}


@router.get('/me')
def get_me(
    current_user: Users = Depends(get_current_user_from_token)
):
    
    return {
        'id': current_user.id,
        'name': current_user.name
    }