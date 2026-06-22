from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    projects: Mapped[List["Projects"]] = relationship(back_populates="user")
    tasks: Mapped[List["Tasks"]] = relationship(back_populates="user")
    subtasks: Mapped[List["SubTasks"]] = relationship(back_populates="user")


class Projects(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(insert_default=datetime.now)
    deadline: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="new")
    priority: Mapped[str] = mapped_column(nullable=False, default="low")

    user: Mapped["Users"] = relationship(back_populates="projects")
    tasks: Mapped[List["Tasks"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class Tasks(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(insert_default=datetime.now)
    deadline: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="new")
    priority: Mapped[str] = mapped_column(nullable=False, default="low")

    user: Mapped["Users"] = relationship(back_populates="tasks")
    project: Mapped["Projects | None"] = relationship(back_populates="tasks")
    subtasks: Mapped[List["SubTasks"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan",
    )


class SubTasks(Base):
    __tablename__ = "subtasks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id"),
        nullable=True,
    )
    title: Mapped[str] = mapped_column(nullable=False)
    created: Mapped[datetime] = mapped_column(insert_default=datetime.now)
    deadline: Mapped[datetime | None] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False, default="new")
    priority: Mapped[str] = mapped_column(nullable=False, default="low")

    user: Mapped["Users"] = relationship(back_populates="subtasks")
    task: Mapped["Tasks | None"] = relationship(back_populates="subtasks")
