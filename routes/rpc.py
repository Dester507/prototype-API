from fastapi import APIRouter, Body
from pydantic import BaseModel

from . import dec


router = APIRouter(prefix='/rpc')


class User(BaseModel):
    age: int
    year: int


@dec(router)
async def test_function(user: User, name: str = Body(...), surname: str = Body(...)):
    return {"msg": f"{name} {surname} {user.age}, {user.year}, you have new msg from Rpc"}


@dec(router)
async def test_function1():
    return {"msg": "Я родився"}
