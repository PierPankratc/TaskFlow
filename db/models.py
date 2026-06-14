from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)

    todos: Mapped[list["Todo"]] = relationship(back_populates='users')

class Todo(Base):
    __tablename__ = 'todo'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped['Users'] = mapped_column(ForeignKey('users.id'))
    task: Mapped[str] = mapped_column()
    status: Mapped[bool] = mapped_column()

    users: Mapped["Users"] = relationship(back_populates="todos")