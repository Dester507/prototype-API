

from fastapi import APIRouter

from . import dec


router = APIRouter()


@dec(router)
async def test_function(name: str):
    return {"msg": f"{name}, you have new msg from Rpc"}
