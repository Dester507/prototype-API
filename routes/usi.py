

from fastapi import APIRouter, Body

from . import dec


router = APIRouter(prefix="/usi")


@dec(router)
async def test_function(name: str = Body(...), surname: str = Body(...)):
    return {"msg": f"{name} {surname}, you have new msg from Usi"}
