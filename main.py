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

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        headers = Headers(scope=scope)
        if "xml" not in headers.get("content-type", ""):
            # if body in json
            return await self.app(scope, receive, send)
        self.receive = receive
        self.send = send
        self.scope = scope
        scope = await self.make_scope()
        await self.app(scope, self.make_receive, self.make_send)

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
        try:
            self.scope["path"], new_body = await Handle(self.message["body"]).handle()
        except:
            raise
        self.message["body"] = dumps(new_body).encode()
        return self.message

    # Edit Url
    async def make_scope(self) -> Scope:
        self.message = await self.receive()
        method_url = await Handle(self.message["body"]).handle(method="url")
        self.scope["path"] = method_url
        return self.scope

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
            body = Handle().build_xml(await Handle().format_success(loads(body)))
            print(body)
            print(len(body))
            headers = MutableHeaders(raw=self.initial_message["headers"])
            headers["Content-Type"] = "application/xml"
            headers["Content_Length"] = str(len(body))
            message["body"] = body
            print(message["body"], headers["Content_Length"])
            await self.send(self.initial_message)
            await self.send(message)


sub_api.add_middleware(CustomMiddleware)


# Test route in main_api
@main_api.post("/test-function")
async def test_function():
    return {"Details": "Test function for main API"}
