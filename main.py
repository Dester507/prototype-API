from typing import Optional

from fastapi import FastAPI, Request

from routes import rpc, system, usi


main_api = FastAPI(title="Main API", description="Foundation")

sub_api = FastAPI(title="SubAPI", description="Base for all routers")

main_api.mount("/api", sub_api)

# Include all routes
sub_api.include_router(rpc.router, prefix='/rpc', tags=['Rpc'])
sub_api.include_router(system.router, prefix='/sys', tags=['System'])
sub_api.include_router(usi.router, prefix='/usi', tags=['Usi'])


# Test route in main_api
@main_api.post("/test-function")
async def test_function():
    return {"Details": "Test function for main API"}


# Middleware that handles body-xml requests
@sub_api.middleware("http")
async def xml_handler_middleware(request: Request, call_next):
    return await call_next(request)
