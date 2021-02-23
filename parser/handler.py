import asyncio

from aiohttp_xmlrpc.common import xml2py, schema, py2xml
from lxml import etree
from starlette.routing import NoMatchFound
from fastapi.responses import Response, JSONResponse


class Handle:
    def __init__(self, xml_body):
        self.xml_body = xml_body
        self.THREAD_POOL_EXECUTOR = None

    async def handle(self):
        xml_request = await self.parse_body()

        full_method_name = xml_request.xpath("//methodName[1]")[0].text
        method_url = await self.lookup_method(full_method_name)

        args = list(
            map(
                xml2py,
                xml_request.xpath("//params/param/value")
            )
        )
        return method_url, args

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

        xml_value.append(py2xml(exception))
        xml_fault.append(xml_value)
        xml_response.append(xml_fault)
        return xml_response

    @staticmethod
    async def lookup_method(full_name):
        from main import sub_api
        try:
            return sub_api.url_path_for(full_name)
        except NoMatchFound:
            print("bad")
            #xml_error = Handle.format_error("Function doesn`t exist")
            return JSONResponse(content="Method doesnt exist")  # FastAPI BAD Response XML



