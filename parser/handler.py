import asyncio
from inspect import signature

from aiohttp_xmlrpc.common import xml2py, schema, py2xml
from lxml import etree
from starlette.routing import NoMatchFound
from fastapi import HTTPException


class Handle:
    def __init__(self, xml_body):
        self.xml_body = xml_body
        self.THREAD_POOL_EXECUTOR = None

    async def handle(self, method="full"):
        xml_request = await self.parse_body()

        full_method_name = xml_request.xpath("//methodName[1]")[0].text
        method_url = await self.lookup_method(full_method_name)
        if method == "url":
            return method_url

        args = list(
            map(
                xml2py,
                xml_request.xpath("//params/param/value")
            )
        )
        ans = {}
        params = [x for x in signature(await self.lookup_endpoint(full_method_name)).parameters.keys()]
        for x in range(len(args)):
            ans[params[x]] = args[x]
        return method_url, ans

    async def parse_body(self):
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                self.THREAD_POOL_EXECUTOR,
                self.parse_xml,
                self.xml_body
            )
        except etree.DocumentInvalid:
            print("Error parse_body")
            raise  # FastAPI BAD Response

    @staticmethod
    def parse_xml(xml_string):
        parse = etree.XMLParser(resolve_entities=False)
        root = etree.fromstring(xml_string, parse)
        schema.assertValid(root)
        return root

    @staticmethod
    def format_error(exception: Exception):
        xml_response = etree.Element("methodResponse")
        xml_fault = etree.Element("fault")
        xml_value = etree.Element("value")

        xml_value.append(py2xml(str(exception)))
        xml_fault.append(xml_value)
        xml_response.append(xml_fault)
        return etree.tostring(xml_response, xml_declaration=True, encoding="utf-8")

    @staticmethod
    async def lookup_method(full_name):
        from main import sub_api
        try:
            return sub_api.url_path_for(full_name)
        except NoMatchFound as ex:
            xml_error = Handle.format_error(ex)
            return HTTPException(status_code=200, detail=xml_error)

    @staticmethod
    async def lookup_endpoint(full_name):
        from main import sub_api
        for route in sub_api.routes:
            if route.name == full_name:
                return route.endpoint
