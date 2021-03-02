from typing import Optional

from fastapi import APIRouter, Body
from pydantic import BaseModel

from . import dec

router = APIRouter(prefix='/rpc')


class User(BaseModel):
    age: int
    year: int


class Item(BaseModel):
    name: str
    count: int


@dec(router)
async def test_function(user: User, name: str = Body(...), surname: str = Body(...)):
    return {"msg": f"{name} {surname} {user.age}, {user.year}, you have new msg from Rpc"}


@dec(router)
async def test_function2(item: Item = Body(..., embed=True)):
    return {"msg": f"Item name -> {item.name}, count -> {item.count}"}


@dec(router)
async def test_function3(item: Item, user: User):
    return {
        "msg": f"User age -> {user.age}, user year reg -> {user.age}, Item name -> {item.name}, count -> {item.count}"}


@dec(router)
async def test_function4(user: User, name: str = Body(...), surname: Optional[str] = Body(None)):
    return {"msg": f"{name} -> User {user.age} {user.year}"} if surname is None else {"msg":
    f"{name} {surname} -> User {user.age}, {user.year}"}


@dec(router)
async def test_function5(name: str = Body(...), surname: Optional[str] = Body(None)):
    return {"msg": f"name -> {name}"} if surname is None else {"msg": f"name -> {name}, surname -> {surname}"}


@dec(router)
async def test_function1():
    return {"msg": "Я родився"}
