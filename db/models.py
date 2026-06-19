from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Table, Column
from datetime import datetime
from typing import List

class Base(DeclarativeBase):
    pass

# ===== ПРОМЕЖУТОЧНАЯ ТАБЛИЦА ДЛЯ СВЯЗИ МНОГИЕ-КО-МНОГИМ =====

# ===== ПОЛЬЗОВАТЕЛИ =====
class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    # Связи: один пользователь → много проектов/задач/подзадач
    projects: Mapped[List["Projects"]] = relationship(back_populates='user')  # ← user, а не users
    tasks: Mapped[List["Tasks"]] = relationship(back_populates='user')
    subtasks: Mapped[List["SubTasks"]] = relationship(back_populates='user')


# ===== ПРОЕКТЫ =====
class Projects(Base):
    __tablename__ = 'projects'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    title: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now())
    deadline: Mapped[datetime] = mapped_column(default=datetime.now())
    status: Mapped[str] = mapped_column(nullable=True)
    priority: Mapped[int] = mapped_column()

    # Связи
    user: Mapped["Users"] = relationship(back_populates="projects")  # ← user (ед.ч.)
    
    # Один проект → много задач (один ко многим)
    tasks: Mapped[List["Tasks"]] = relationship(back_populates="project")  # ← project (ед.ч.)


# ===== ЗАДАЧИ =====
class Tasks(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    project_id: Mapped[int] = mapped_column(ForeignKey('projects.id'), default=0)
    title: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now())
    deadline: Mapped[datetime] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column()
    priority: Mapped[int] = mapped_column()

    # Связи
    user: Mapped["Users"] = relationship(back_populates="tasks")  # ← user (ед.ч.)
    project: Mapped["Projects"] = relationship(back_populates="tasks")  # ← project (ед.ч.)
    
    # Если нужна связь многие-ко-многим с проектами (через промежуточную таблицу)
    # projects: Mapped[List["Projects"]] = relationship(
    #     secondary=task_project_association,
    #     back_populates="tasks"
    # )
    
    # Одна задача → много подзадач
    subtasks: Mapped[List["SubTasks"]] = relationship(back_populates='task')


# ===== ПОДЗАДАЧИ =====
class SubTasks(Base):
    __tablename__ = 'subtasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    task_id: Mapped[int] = mapped_column(ForeignKey('tasks.id'), default=0) 
    title: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(default=datetime.now())
    deadline: Mapped[datetime] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column()
    priority: Mapped[int] = mapped_column()

    # Связи
    user: Mapped["Users"] = relationship(back_populates="subtasks")  # ← user (ед.ч.)
    task: Mapped["Tasks"] = relationship(back_populates="subtasks")  # ← task (ед.ч.)


