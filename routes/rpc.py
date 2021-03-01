from fastapi import APIRouter, Body

from . import dec


router = APIRouter(prefix='/rpc')


@dec(router)
async def test_function(name: str = Body(...), surname: str = Body(...)):
    return {"msg": f"{name} {surname}, you have new msg from Rpc"}


@dec(router)
async def test_function1():
    return {"msg": "Я родився"}
