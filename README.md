# TaskFlow API

Pet-project — REST API для управления проектами, задачами и подзадачами. Иерархия данных: **Проект → Задача → Подзадача**. Каждый пользователь работает только со своими сущностями.

## Возможности

- Регистрация и вход через один эндпоинт `/login`
- JWT-аутентификация через cookie (`access_token`)
- Хэширование паролей (bcrypt)
- CRUD для проектов, задач и подзадач
- Статусы: `new`, `in_progress`, `done`
- Приоритеты: `low`, `middle`, `high`
- Удаление с подтверждением (`?confirm=true`)
- Автодокументация: Swagger UI и ReDoc
- Тесты на pytest с in-memory SQLite

## Технологии

| Компонент | Технология |
|-----------|------------|
| Язык | Python 3.11+ |
| Фреймворк | FastAPI |
| ORM | SQLAlchemy 2.x |
| Миграции | Alembic |
| Аутентификация | AuthX (JWT в cookie) |
| Пароли | bcrypt |
| Валидация | Pydantic 2.x |
| БД | SQLite (`todo.db`) |
| Сервер | Uvicorn |
| Тесты | pytest, httpx |
| Контейнеризация | Docker |

## Структура проекта

```
fastapi/
├── api/
│   ├── password.py          # хэширование и проверка паролей
│   ├── schemas.py           # Pydantic-схемы запросов
│   └── routers/
│       ├── auth.py          # логин / регистрация
│       ├── projects.py      # проекты
│       ├── tasks.py         # задачи
│       └── subtasks.py      # подзадачи
├── db/
│   ├── create_db.py         # подключение к БД, сессия
│   └── models.py            # SQLAlchemy-модели
├── tests/
│   ├── conftest.py          # фикстуры (тестовая БД, клиент)
│   ├── test_auth.py
│   ├── test_projects.py
│   ├── test_tasks.py
│   └── test_subtasks.py
├── alembic/                 # миграции БД
├── main.py                  # точка входа FastAPI
├── requirements.txt
├── pytest.ini
├── pyrightconfig.json
├── dockerfile
├── todo.db                  # локальная БД (создаётся при запуске)
└── README.md
```

## Установка и запуск

```bash
git clone https://github.com/PierPankratc/TaskFlow.git
cd fastapi

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

После запуска:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Аутентификация

1. Отправьте `POST /login` с телом:

```json
{
  "name": "user",
  "password": "secret123"
}
```

2. В ответе придёт `token`, а в cookie — `access_token`.
3. Для защищённых эндпоинтов cookie передаётся автоматически (браузер / клиент с поддержкой cookies).

Если пользователя нет — он создаётся. Пароль сохраняется в виде bcrypt-хэша.

## API-эндпоинты

### Пользователи

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | `/login` | Вход / регистрация | — |

### Проекты (`/project`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | `/project/add` | Создать проект | cookie |
| GET | `/projectget_all` | Все проекты пользователя | cookie |
| GET | `/project/three/{project_id}` | Проект с задачами и подзадачами | cookie |
| DELETE | `/project/del/{project_id}` | Удалить (`?confirm=true`) | cookie |

### Задачи (`/tasks`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | `/tasks/add` | Создать задачу | cookie |
| GET | `/tasksget_all` | Все задачи пользователя | cookie |
| GET | `/tasks/task/{task_id}` | Задача с подзадачами | cookie |
| DELETE | `/tasks/del/{task_id}` | Удалить (`?confirm=true`) | cookie |

### Подзадачи (`/subtasks`)

| Метод | Путь | Описание | Auth |
|-------|------|----------|------|
| POST | `/subtasks/add` | Создать подзадачу | cookie |
| GET | `/subtasksget_all` | Все подзадачи пользователя | cookie |
| DELETE | `/subtasks/del/{task_id}` | Удалить (`?confirm=true`) | cookie |

## Тесты

```bash
pytest tests/ -v
```

Тесты используют SQLite in-memory и не затрагивают файл `todo.db`.

## Docker

```bash
docker build -t taskflow-api -f dockerfile .

docker run -d -p 8000:8000 --name taskflow taskflow-api

docker stop taskflow
docker rm taskflow
```

## Планы на будущее

- [ ] Переход на PostgreSQL
- [ ] Сортировка, фильтрация и пагинация
- [ ] Эндпоинты обновления (PUT/PATCH)


## Лицензия

MIT

## Автор

PierPankratc
