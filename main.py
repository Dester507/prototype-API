from json import dumps, loads

from fastapi import FastAPI
from starlette.types import Scope, Receive, Send, ASGIApp, Message
from starlette.datastructures import Headers, MutableHeaders

from routes import rpc, system, usi
from parser_custom import Handle


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
        self.initial_message: Message = {}
        self.message = None
        self.error_status = False
        self.error = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        headers = Headers(scope=scope)
        if "xml" not in headers.get("content-type", ""):
            # if body in json
            return await self.app(scope, receive, send)
        self.receive = receive
        self.send = send
        self.scope = await self.make_scope(scope)
        await self.app(self.scope, self.make_receive, self.make_send)

    # Edit Body
    async def make_receive(self) -> Message:
        assert self.message["type"] == "http.request"
        body = self.message["body"]
        more_body = self.message.get("more_body", False)
        if more_body:
            self.message = await self.receive()
            if body != b"":
                raise NotImplementedError(
                    "Streaming the request body isn`t supported yet"
                )
        if not self.error_status:
            try:
                new_body = await Handle(self.message["body"]).handle()
                self.message["body"] = dumps(new_body).encode()
                return self.message
            except Exception as ex:
                self.error_status = True
                self.error = ex
        else:
            return self.message

    # Edit Url
    async def make_scope(self, scope: Scope) -> Scope:
        self.message = await self.receive()
        try:
            method_url = await Handle(self.message["body"]).handle(method="url")
            scope["path"] = method_url
            return scope
        except Exception as ex:
            self.error_status = True
            self.error = ex
            return scope

    # Edit Response
    async def make_send(self, message: Message) -> None:
        if message["type"] == "http.response.start":
            headers = Headers(raw=message["headers"])
            if headers["content-type"] != "application/json":
                await self.send(message)
                return
            self.initial_message = message
        elif message["type"] == "http.response.body":
            body = message.get("body", b"")
            more_body = message.get("more_body", False)
            if more_body:
                raise NotImplementedError(
                    "Streaming the response body isn`t supported yet"
                )
            if not self.error_status:
                body = Handle().build_xml(await Handle().format_success(loads(body)))
            else:
                body = Handle().build_xml(await Handle().format_error(self.error))
                self.initial_message["status"] = 200
                self.error_status = False
                self.error = None
            headers = MutableHeaders(raw=self.initial_message["headers"])
            headers["Content-Type"] = "application/xml"
            headers["Content-Encoding"] = "utf-8"
            headers["Content-Length"] = str(len(body))
            message["body"] = body
            await self.send(self.initial_message)
            await self.send(message)


sub_api.add_middleware(CustomMiddleware)


# Test route in main_api
@main_api.post("/test-function")
async def test_function():
    return {"Details": "Test function for main API"}
