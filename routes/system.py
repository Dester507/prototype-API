

from fastapi import APIRouter

from . import dec


router = APIRouter(prefix="/system")


@dec(router)
async def test_function(name: str):
    return {"msg": f"{name}, you have new msg from System"}
