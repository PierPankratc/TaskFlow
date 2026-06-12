from fastapi import APIRouter, Depends
from db.create_db import get_db_connect # create_db импортировать необязательно, он уже вызван
from api.schemas import UserSchema, TaskSchema
from sqlalchemy.orm import Session
from db.models import Users, Todo

router = APIRouter(prefix='/user', tags=['Пользователи'])

@router.post('/login')
def login(user: UserSchema, db: Session = Depends(get_db_connect)):
    # Ищем пользователя по имени
    new_user = db.query(Users).filter(Users.name == user.name).first() 
    if new_user:
        authorizetad_user =  db.query(Users).filter(Users.name == user.name and Users.password == user.password).first()
        if not authorizetad_user:
             return {'User': user.name,
                     'creditionals': {'user.name': 'access',
                     'password': 'incorrect'    
                     }}
       
        return {'Auth': True, 'user_id': authorizetad_user.id}
    else:
        # Создаём нового пользователя
        new_user = Users(name=user.name)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {'Auth': True, 'user_id': new_user.id, 'message': 'Пользователь создан'}
    
@router.post('/add_task/{id}')
def add_task( task: TaskSchema, db: Session = Depends(get_db_connect), id: Depends(login()['user_id'])):
        user = db.query(Users).filter(Users.id == id).first()
        if not user:
             return {'User': None}
        new_task = Todo(
             task = task.task,
             status = task.status if task.status else False,
             user_id = id 
        )
        db.add(new_task)
        db.commit()
        return {
        'id': new_task.id,
        'task': new_task.task,
        'status': new_task.status,
        'user_id': new_task.user_id
        }
@router.get('/tasks/{id}')
def get_tasks(id: int, db: Session = Depends(get_db_connect)):
    user = db.query(Users).filter(Users.id == id).first()
    if not user:
        return {'User': 'Not Found'}
    # ИСПРАВЛЕНО: было user.todo, нужно user.todos
    task_list = []
    for task in user.todos:
         task_list.append ({
               len(task_list)+1: task.task,
               'status': task.status
         })
    return task_list
      # Возвращает список задач пользователя


@router.put('/update_task/{task_id}')
def upd_task(task_id: int, new_task: str, db: Session = Depends(get_db_connect)):
    task = db.query(Todo).filter(Todo.id == task_id).first()
    if not task:
         return {'task': None}
    task.task = new_task
    db.commit()
    return {'id': task.id, 'task': task.task, 'status': task.status}

@router.delete('/detete/{task_id}')
def delete_task(task_id: int, confirm: bool = False, db: Session = Depends(get_db_connect)):
    task = db.query(Todo).filter(Todo.id == task_id).first()
    if not task:
         return {'task': None}
    
    if not confirm:
        return {
            'warning': 'Вы уверены?',
            'action': f'DELETE /tasks/{task_id}?confirm=true'
        }

    db.delete(task)
    db.commit()
    return {'message': f'Task {task_id} deleted'}




