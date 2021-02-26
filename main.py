from json import dumps, loads

from fastapi import FastAPI
from starlette.types import Scope, Receive, Send, ASGIApp, Message
from starlette.datastructures import Headers, MutableHeaders
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
        self.initial_message: Message = {}
        self.should_decode_from_msgpack_to_json = False
        self.should_encode_from_json_to_msgpack = False

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
        bb = b'''<?xml version="1.0" encoding="ASCII"?>
<methodCall>
    <methodName>rpc_test_function</methodName>
    <params>
        <param>
            <value>
                <string>
                    Tolik
                </string>
            </value>
        </param>

        <param>
            <value>
                <string>
                    Demchuk
                </string>
            </value>
        </param>
    </params>
</methodCall>'''
        scope["path"] = await Handle(bb).handle()
        # request.body = b'{\n    "name": "Tolik",\n    "surname": "Demchuk"\n}\n'
        await self.app(scope, self.make_receive, self.send)

    async def make_receive(self) -> Message:
        message = await self.receive()
        if not self.should_decode_from_msgpack_to_json:
            return message
        assert message["type"] == "http.request"
        body = message["body"]
        more_body = message.get("more_body", False)
        print(body)
        if more_body:
            message = await self.receive()
            if message["body"] != b"":
                raise NotImplementedError(
                    "Streaming the request body isn`t supported yet"
                )
        message["body"] = dumps({"name": "vlad", "surname": "Dester"}).encode()
        print(message["body"])
        return message

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


# Middleware that handles body-xml requests
@sub_api.middleware("http")
async def xml_handler_middleware(request: Request, call_next):
    return await call_next(request)
