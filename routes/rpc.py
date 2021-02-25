

from fastapi import APIRouter
from pydantic import BaseModel

from . import dec


router = APIRouter(prefix='/rpc')


class User(BaseModel):
    name: str
    surname: str


@dec(router)
async def test_function(user: User):
    return {"msg": f"{user.name} {user.surname}, you have new msg from Rpc"}


@dec(router)
async def test_function1():
    return {"msg": "Я родився"}
