from json import dumps

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.types import Scope, Receive, Send, ASGIApp, Message
from starlette.datastructures import Headers

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
        self.initial_message: Message = {}
        self.should_decode_from_msgpack_to_json = False
        self.should_encode_from_json_to_msgpack = False
        self.message = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        headers = Headers(scope=scope)
        self.should_decode_from_msgpack_to_json = (
            "application/x-msgpack" in headers.get("content-type", "")
        )
        self.should_encode_from_json_to_msgpack = (
            "application/x-msgpack" in headers.getlist("accept")
        )
        self.receive = receive
        self.send = send
        self.scope = scope
        scope = await self.make_scope()
        await self.app(scope, self.make_receive, self.send)

    async def make_receive(self) -> Message:
        if not self.should_decode_from_msgpack_to_json:
            return self.message
        assert self.message["type"] == "http.request"
        body = self.message["body"]
        more_body = self.message.get("more_body", False)
        if more_body:
            self.message = await self.receive()
            if body != b"":
                raise NotImplementedError(
                    "Streaming the request body isn`t supported yet"
                )
        self.scope["path"], new_body = await Handle(self.message["body"]).handle()
        self.message["body"] = dumps(new_body).encode()
        return self.message

    async def make_scope(self) -> Scope:
        self.message = await self.receive()
        method_url = await Handle(self.message["body"]).handle(method="url")
        if method_url is None:
            pass
            # return JSONResponse(content="Method doesnt exists")
        else:
            self.scope["path"] = method_url
            return self.scope

    # async def make_send(self, message: Message) -> None:
    #     if not self.should_encode_from_json_to_msgpack:
    #         await self.send(message)
    #         return
    #     if message["type"] == "http.response.start":
    #         headers = Headers(raw=message["headers"])
    #         if headers["content-type"] != "application/json":
    #             self.should_encode_from_json_to_msgpack = False
    #             await self.send(message)
    #             return
    #         self.initial_message = message
    #     elif message["type"] == "http.response.body":
    #         assert self.should_encode_from_json_to_msgpack
    #         body = message.get("body", b"")
    #         more_body = message.get("more_body", False)
    #         if more_body:
    #             raise NotImplementedError(
    #                 "Streaming the response body isn`t supported yet"
    #             )
    #         body = msgpack.packb(loads(body))
    #         print(body)
    #         headers = MutableHeaders(raw=self.initial_message["headers"])
    #         headers["Content-Type"] = "application/x-msgpack"
    #         headers["Content_Length"] = str(len(body))
    #         message["body"] = body
    #         await self.send(self.initial_message)
    #         await self.send(message)


sub_api.add_middleware(CustomMiddleware)


# Test route in main_api
@main_api.post("/test-function")
async def test_function():
    return {"Details": "Test function for main API"}
