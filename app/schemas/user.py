from pydantic import BaseModel, ConfigDict


class UserBase(BaseModel):
    login: str


class UserCreate(UserBase):
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(UserBase):
    id: int
    role: str

    model_config = ConfigDict(from_attributes=True)
