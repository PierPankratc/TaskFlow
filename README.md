
# Todo List API на FastAPI

REST API для управления задачами с аутентификацией пользователей.

##  Возможности

- ✅ Регистрация и аутентификация пользователей (JWT)
- ✅ Создание, просмотр, обновление и удаление задач
- ✅ Каждый пользователь видит только свои задачи
- ✅ Подтверждение перед удалением задач
- ✅ Docker 

##  Технологии

- **Python** 3.11+
- **FastAPI** — веб-фреймворк
- **SQLAlchemy** — ORM для работы с БД
- **SQLite** — база данных (можно заменить на PostgreSQL)
- **JWT** — аутентификация
- **Pydantic** — валидация данных
- **Uvicorn** — ASGI сервер
- **Docker** — контейнеризация

##  Структура проекта


fastapi/
├── api/
│   ├── __init__.py
│   └── routers/
│       ├── __init__.py
│       └── users.py          
├── db/
│   ├── __init__.py
│   ├── create_db.py          
│   └── models.py             
├── alembic/                   
├── main.py                    
├── requirements.txt           
├── Dockerfile                 
└── README.md                


##  Установка и запуск

bash
```
git clone https://github.com/PierPankratc/fastapi.git
```
```
cd fastapi
```


bash
```
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate      # Windows
```


bash
```
pip install -r requirements.txt
```


bash
```
uvicorn main:app --reload
```


- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc


##  API Эндпоинты

### Аутентификация

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/user/login` | Логин/регистрация, получение JWT токена |

### Задачи

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/user/add_task` | Создать задачу | ✅  |
| GET | `/user/my_tasks` | Получить все свои задачи | ✅  |
| PUT | `/user/update_task/{task_id}` | Обновить задачу | ✅  |
| DELETE | `/user/delete_task/{task_id}` | Удалить задачу (с подтверждением) | ✅  |
| GET | `/user/me` | Информация о текущем пользователе | ✅  |


##  Зависимости (requirements.txt)

```
fastapi==0.115.0
uvicorn==0.30.0
sqlalchemy==2.0.35
pydantic==2.9.0
pyjwt==2.8.0
python-dotenv==1.0.0
```

##  Можно добавить в дальнейшем

- [ ] Хеширование паролей (bcrypt)
- [ ] Переход на PostgreSQL
- [ ] Добавить поле "deadline" для задач
- [ ] Сортировка и фильтрация задач
- [ ] Пагинация
- [ ] Переменные окружения для секретов
- [ ] Тесты 

##  Лицензия

MIT

##  Автор

PierPankratc


