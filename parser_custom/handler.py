import asyncio
from inspect import signature

from aiohttp_xmlrpc.common import xml2py, schema, py2xml
from lxml import etree
from starlette.routing import NoMatchFound

import exceptions


class Handle:
    def __init__(self, xml_body=None):
        self.xml_body = xml_body
        self.THREAD_POOL_EXECUTOR = None

    async def handle(self, method="full"):
        try:
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
            return ans
        except Exception:
            raise

    async def parse_body(self):
        loop = asyncio.get_event_loop()
        try:
            return await loop.run_in_executor(
                self.THREAD_POOL_EXECUTOR,
                self.parse_xml,
                self.xml_body
            )
        except etree.DocumentInvalid:
            raise exceptions.ParseError("Caught ParseError while parse the xml-body")

    @staticmethod
    def parse_xml(xml_string):
        parse = etree.XMLParser(resolve_entities=False)
        root = etree.fromstring(xml_string, parse)
        schema.assertValid(root)
        return root

    @staticmethod
    async def format_error(exception: Exception):
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
            raise exceptions.MethodNotFound(f"Method {full_name} does not exist")

    @staticmethod
    async def lookup_endpoint(full_name):
        from main import sub_api
        for route in sub_api.routes:
            if route.name == full_name:
                return route.endpoint
        raise exceptions.MethodNotFound(f"Route for method {full_name} does not exists")

    @staticmethod
    async def format_success(body):
        xml_response = etree.Element("methodResponse")
        xml_params = etree.Element("params")
        xml_param = etree.Element("param")
        xml_value = etree.Element("value")

        xml_value.append(py2xml(body))
        xml_param.append(xml_value)
        xml_params.append(xml_param)
        xml_response.append(xml_params)
        return xml_response

    @staticmethod
    def build_xml(tree):
        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            )
