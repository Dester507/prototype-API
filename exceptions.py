from lxml import etree

from aiohttp_xmlrpc.common import py2xml


class XMLRPCError(Exception):
    code = -32500

    @property
    def message(self):
        return self.args[0]

    @property
    def name(self):
        return self.__class__.__name__

    def __repr__(self):
        return "{0.name}({0.message})".format(self)


class ParseError(XMLRPCError):
    code = -32700


class UnsupportedEncodingError(ParseError):
    code = -32701


class InvalidCharacterError(ParseError):
    code = -32702


class ServerError(XMLRPCError):
    code = -32603


class InvalidData(ServerError):
    code = -32600


class MethodNotFound(ServerError):
    code = -32601


class InvalidArguments(ServerError):
    code = -32602


class ApplicationError(XMLRPCError):
    code = -32500


class SystemError(XMLRPCError):
    code = -32400


class TransportError(XMLRPCError):
    code = -32300


__EXCEPTION_CODES = {
    -32000: Exception,
    XMLRPCError.code: XMLRPCError,
    ParseError.code: ParseError,
    UnsupportedEncodingError.code: UnsupportedEncodingError,
    InvalidCharacterError.code: InvalidCharacterError,
    ServerError.code: ServerError,
    InvalidData.code: InvalidData,
    MethodNotFound.code: MethodNotFound,
    InvalidArguments.code: InvalidArguments,
    ApplicationError.code: ApplicationError,
    SystemError.code: SystemError,
    TransportError.code: TransportError,
}

__EXCEPTION_TYPES = {value: key for key, value in __EXCEPTION_CODES.items()}


@py2xml.register(Exception)
def _(value):
    code, reason = __EXCEPTION_TYPES[Exception], repr(value)
    for klass in value.__class__.__mro__:
        if klass in __EXCEPTION_TYPES:
            code = __EXCEPTION_TYPES[klass]
            break

    struct = etree.Element("struct")

    for key, value in (("faultCode", code), ("faultString", reason)):
        member = etree.Element("member")
        struct.append(member)

        key_el = etree.Element("name")
        key_el.text = key
        member.append(key_el)

        value_el = etree.Element("value")
        value_el.append(py2xml(value))
        member.append(value_el)

    # struct.attrib['error'] = '1'
    return struct
