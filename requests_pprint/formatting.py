import json
from xml.dom.minidom import parseString

from aiohttp import ClientResponse, ContentTypeError
from multidict import CIMultiDict, CIMultiDictProxy
from requests import Response
from requests.structures import CaseInsensitiveDict


def format_headers(
    headers: dict | CaseInsensitiveDict | CIMultiDict | CIMultiDictProxy,
) -> str:
    """
    Format headers for pretty printing.

    Args:
        headers (dict | CaseInsensitiveDict | CIMultiDict | CIMultiDictProxy): The headers to format.

    Returns:
        str: The formatted headers as a string.
    """
    return "\r\n".join(f"[b]{k}[/]: {v}" for k, v in headers.items())


def format_http_message(
    start_marker: str, first_line: str, headers: str, body: str, end_marker: str
) -> str:
    """Format an HTTP message for pretty printing.

    Args:
        start_marker (str): Marker to indicate the start of the message.
        first_line (str): The request/response line of the HTTP message.
        headers (str): The HTTP headers as a single string.
        body (str): The HTTP body.
        end_marker (str): Marker to indicate the end of the message.

    Returns:
        str: The formatted HTTP message as a string.
    """
    return "{}\n{}\r\n{}\r\n\r\n{}\n{}".format(
        start_marker, first_line, headers, body, end_marker
    )


def parse_body(body: bytes | str | None) -> str:
    """
    Parse the body of an HTTP message.

    Args:
        body (bytes | str | None): The body of the HTTP message.

    Returns:
        str: The parsed body as a string.
    """
    if isinstance(body, bytes):
        return body.decode()
    return body or ""


def parse_content(
    content_type: str,
    content: bytes,
    content_text: str,
    content_json: dict,
    content_encoding: str = "utf-8",
) -> str | bytes:
    """
    Parse raw content based on content type and encoding.

    Args:
        content_type (str): The content type of the response.
        content (bytes): The raw content of the response.
        content_text (str): The text content of the response.
        content_json (dict): The JSON content of the response.
        content_encoding (str): The encoding of the content.

    Returns:
        str | bytes: The parsed content.
    """
    # Check for BOM and decode with UTF-8-SIG if present
    if content.startswith(b"\xef\xbb\xbf"):
        return content.decode("utf-8-sig")
    # JSON handling
    elif "application/json" in content_type:
        try:
            return json.dumps(content_json, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            return content.decode("utf-8", errors="replace")
    # XML handling
    elif "application/xml" in content_type or "text/xml" in content_type:
        try:
            dom = parseString(content)
            return dom.toprettyxml()
        except Exception:
            return content.decode("utf-8", errors="replace")
    # Binary or image content
    elif "application/octet-stream" in content_type or content_type.startswith(
        "image/"
    ):
        return content
    # Encoding detection if no BOM is present
    if content_encoding:
        try:
            return content.decode(content_encoding)
        except (UnicodeDecodeError, TypeError):
            pass  # Fallback to default decoding below

    # Fallback to UTF-8 or raw decoding
    return content_text or content.decode("utf-8", errors="replace")


async def async_parse_body(body: bytes | None) -> str:
    """
    Parse the body of an async HTTP message.

    Args:
        body (bytes | None): The body of the HTTP message.

    Returns:
        str: The parsed body as a string.
    """
    if body is None:
        return ""
    return body.decode()


def parse_response_body(response: Response) -> str | bytes:
    """
    Parse the body of an HTTP response (synchronous).

    Args:
        response (requests.models.Response): The response to parse.

    Returns:
        str | bytes: The parsed body of the response.
    """
    content_type: str = response.headers.get("Content-Type", "").lower()
    content_encoding: str = response.apparent_encoding
    content: bytes = response.content
    try:
        content_text: str = response.text
    except UnicodeDecodeError:
        content_text = ""
    try:
        content_json: dict = response.json()
    except json.JSONDecodeError:
        content_json = {}

    return parse_content(
        content_type, content, content_text, content_json, content_encoding
    )


async def async_parse_response_body(response: ClientResponse) -> str | bytes:
    """
    Parse the body of an HTTP response (asynchronous).

    Args:
        response (aiohttp.ClientResponse): The response to parse.

    Returns:
        str | bytes: The parsed body of the response.
    """
    content_type: str = response.headers.get("Content-Type", "").lower()
    content_encoding: str = response.get_encoding()
    content: bytes = await response.read()
    try:
        content_text: str = await response.text()
    except UnicodeDecodeError:
        content_text = ""
    try:
        content_json: dict = await response.json()
    except (json.JSONDecodeError, ContentTypeError):
        content_json = {}

    return parse_content(
        content_type, content, content_text, content_json, content_encoding
    )