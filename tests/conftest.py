import asyncio
import json
from typing import Optional
from unittest.mock import Mock

import pytest
import pytest_asyncio
from aiohttp import ClientRequest, ClientResponse, RequestInfo
from multidict import CIMultiDict, CIMultiDictProxy
from requests.models import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict
from yarl import URL


def make_response(
    method: str,
    url: str,
    status: int,
    reason: str,
    headers: dict[str, str],
    request_info: RequestInfo,
    history: Optional[tuple[ClientResponse]] = None,
) -> ClientResponse:
    """Utility to create a fake aiohttp ClientResponse."""
    if history is None:
        history = tuple()

    resp = ClientResponse(
        method=method,
        url=URL(url),
        writer=None,
        continue100=None,
        timer=None,  # type: ignore
        request_info=request_info,
        traces=[],
        loop=asyncio.get_event_loop(),
        session=Mock(),
    )

    # Set status, reason, headers and history
    resp.status = status
    resp.reason = reason
    resp._headers = CIMultiDictProxy(CIMultiDict(headers))
    resp._raw_headers = tuple(
        (k.encode(), v.encode()) for k, v in resp._headers.items()
    )
    resp._history = history

    resp_body_headers: dict[str, str] = dict(request_info.headers.copy())
    resp_body_headers["X-Amzn-Trace-Id"] = "Root=1-test"

    # Fake body content (matches httpbin.org format)
    body_dict = {
        "args": {},
        "headers": resp_body_headers,
        "origin": "xx.xx.xx.xx",
        "url": url,
    }
    fake_body: bytes = json.dumps(body_dict, indent=2).encode("utf-8")

    # Patch the .read() method so it returns our fake body
    async def _fake_read() -> bytes:
        return fake_body

    resp.read = _fake_read  # type: ignore

    # Also patch get_encoding for parse_response_body
    resp.get_encoding = lambda: "utf-8"

    return resp


@pytest.fixture
def sync_request() -> PreparedRequest:
    req = PreparedRequest()
    req.method = "GET"
    req.url = "https://example.com"
    req.headers = CaseInsensitiveDict({"User-Agent": "Mozilla/5.0"})
    req.body = b'{"key": "value"}'
    return req


@pytest.fixture
def sync_response() -> Response:
    resp = Response()
    resp.status_code = 200
    resp.reason = "OK"
    resp.headers = CaseInsensitiveDict({"Content-Type": "application/json"})
    resp._content = b'{"status": "success"}'
    return resp


@pytest_asyncio.fixture
async def async_request() -> ClientRequest:
    headers: CIMultiDict[str] = CIMultiDict({"User-Agent": "Mozilla/5.0"})
    url = URL("https://example.com")
    req = ClientRequest(method="GET", url=url, headers=headers)
    req.update_body_from_data(json.dumps({"key": "value"}).encode())
    return req


@pytest_asyncio.fixture
async def async_response() -> ClientResponse:
    url = "https://httpbin.org/get"

    req_headers: dict[str, str] = {
        "Host": "httpbin.org",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Python/3.9 aiohttp/3.12.15",
    }
    request_info = RequestInfo(
        url=URL(url),
        method="GET",
        headers=CIMultiDictProxy(CIMultiDict(req_headers)),
        real_url=URL(url),
    )

    return make_response(
        method="GET",
        url=url,
        status=200,
        reason="OK",
        headers={
            "Date": "Mon, 11 Aug 2025 10:13:53 GMT",
            "Content-Type": "application/json",
            "Content-Length": "418",
            "Connection": "keep-alive",
            "Server": "gunicorn/19.9.0",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        request_info=request_info,
    )


@pytest_asyncio.fixture
async def async_redirected_response(async_response: ClientResponse) -> ClientResponse:
    url = "https://httpbin.org/redirect/1"

    req_headers: dict[str, str] = {
        "Host": "httpbin.org",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "Python/3.9 aiohttp/3.12.15",
    }
    request_info = RequestInfo(
        url=URL(url),
        method="GET",
        headers=CIMultiDictProxy(CIMultiDict(req_headers)),
        real_url=URL(url),
    )

    resp: ClientResponse = make_response(
        method="GET",
        url=url,
        status=302,
        reason="Found",
        headers={
            "Date": "Mon, 11 Aug 2025 10:47:33 GMT",
            "Content-Type": "text/html; charset=utf-8",
            "Content-Length": "215",
            "Connection": "keep-alive",
            "Server": "gunicorn/19.9.0",
            "Location": "/get",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        request_info=request_info,
    )

    final_resp = async_response
    final_resp._history = (resp,)

    return final_resp
