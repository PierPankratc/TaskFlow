from pydantic import BaseModel, Field

class UserSchema(BaseModel):
    name: str
    password: str = Field(min_length=10, max_length=30)

class TaskSchema(BaseModel):
    task: str
    status: bool = Field(default=False)
    model_config = {'extra': 'forbid'}                                                            

