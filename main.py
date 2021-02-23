from typing import Optional

from fastapi import FastAPI
from starlette.types import Scope, Receive, Send, ASGIApp
from starlette.requests import Request

from routes import rpc, system, usi
from parser.handler import Handle


main_api = FastAPI(title="Main API", description="Foundation")

sub_api = FastAPI(title="SubAPI", description="Base for all routers")

main_api.mount("/api", sub_api)

# Include all routes
sub_api.include_router(rpc.router, tags=['Rpc'])
sub_api.include_router(system.router, tags=['System'])
sub_api.include_router(usi.router, tags=['Usi'])


# Custom middleware
class CustomMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        request = Request(scope, receive=receive)
        scope["path"], args = await Handle(await request.body()).handle()
        await self.app(scope, receive, send)


sub_api.add_middleware(CustomMiddleware)


# Test route in main_api
@main_api.post("/test-function")
async def test_function():
    return {"Details": "Test function for main API"}


# Middleware that handles body-xml requests
@sub_api.middleware("http")
async def xml_handler_middleware(request: Request, call_next):
    return await call_next(request)
