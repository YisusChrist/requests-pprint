import json

from aiohttp import ClientResponse
from multidict import CIMultiDict, CIMultiDictProxy
from requests import Response
from requests.structures import CaseInsensitiveDict


def format_headers(
    headers: dict | CaseInsensitiveDict | CIMultiDict | CIMultiDictProxy,
) -> str:
    """Format headers for pretty printing."""
    return "\r\n".join(f"[b]{k}[/]: {v}" for k, v in headers.items())


def format_http_message(
    start_marker: str, first_line: str, headers: str, body: str, end_marker: str
) -> str:
    """Format an HTTP message for pretty printing."""
    return "{}\n{}\r\n{}\r\n\r\n{}\n{}".format(
        start_marker, first_line, headers, body, end_marker
    )


def parse_body(body: bytes | str | None) -> str:
    """Parse the body of an HTTP message."""
    if isinstance(body, bytes):
        return body.decode()
    return body or ""


def parse_response_body(response: Response) -> str:
    """Parse the body of an HTTP response."""
    try:
        return json.dumps(json.loads(response.text), indent=2)
    except json.decoder.JSONDecodeError:
        return response.text or response.content.decode()


async def async_parse_body(body: bytes | None) -> str:
    """Parse the body of an async HTTP message."""
    if body is None:
        return ""
    return body.decode()


async def async_parse_response_body(response: ClientResponse) -> str:
    """Parse the body of an async HTTP response."""
    response_body: str = await response.text()
    try:
        return json.dumps(json.loads(response_body), indent=2)
    except json.decoder.JSONDecodeError:
        return response_body
