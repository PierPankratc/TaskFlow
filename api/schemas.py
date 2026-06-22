from typing import Literal

from pydantic import BaseModel, Field
from datetime import datetime

class UserSchema(BaseModel):
    name: str
    password: str = Field( max_length=30)
    
    model_config = {'extra': 'forbid'}   

class ProjectSchema(BaseModel):
    title: str = Field(max_length=50)
    created: datetime | None = None
    deadline: datetime | None = None
    status: Literal["new", "in_progress", "done"] = "new"
    priority: Literal['low', 'middle', 'high'] = 'low'
    
    model_config = {'extra': 'forbid'} 


class TaskSchema(BaseModel):
    title: str = Field(max_length=50)
    project_id: int | None = None
    deadline: datetime | None = None
    status: Literal["new", "in_progress", "done"] = "new"
    priority: Literal['low', 'middle', 'high'] = 'low'
    
    model_config = {'extra': 'forbid'} 

class SubTaskSchema(BaseModel):
    title: str = Field(max_length=50)
    task_id: int | None = None
    deadline: datetime | None = None
    status: Literal["new", "in_progress", "done"] = "new"
    priority: Literal['low', 'middle', 'high'] = 'low'
    
    model_config = {'extra': 'forbid'} 
