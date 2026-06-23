from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    role: str

    # Режим совместимости с ORM
    model_config = ConfigDict(from_attributes=True)
