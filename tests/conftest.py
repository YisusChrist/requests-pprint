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

req_url = "https://httpbin.org"
req_headers: dict[str, str] = {
    "Host": "httpbin.org",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate",
    "User-Agent": "Python/3.9 aiohttp/3.12.15",
}
resp_headers: dict[str, str] = {
    "Date": "Mon, 11 Aug 2025 10:13:53 GMT",
    "Content-Type": "application/json",
    "Content-Length": "418",
    "Connection": "keep-alive",
    "Server": "gunicorn/19.9.0",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Credentials": "true",
}


def make_request(url: str) -> RequestInfo:
    return RequestInfo(
        url=URL(url),
        method="GET",
        headers=CIMultiDictProxy(CIMultiDict(req_headers)),
        real_url=URL(url),
    )


def make_response_body(url: str) -> bytes:
    resp_body_headers: dict[str, str] = dict(req_headers.copy())
    resp_body_headers["X-Amzn-Trace-Id"] = "Root=1-test"

    # Fake body content (matches httpbin.org format)
    body_dict = {
        "args": {},
        "headers": resp_body_headers,
        "origin": "xx.xx.xx.xx",
        "url": url,
    }
    return json.dumps(body_dict, indent=2).encode("utf-8")


def make_response(
    method: str,
    url: str,
    status: int,
    reason: str,
    request_info: RequestInfo,
    headers: Optional[dict[str, str]] = None,
) -> ClientResponse:
    """Utility to create a fake aiohttp ClientResponse."""
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
    resp._headers = CIMultiDictProxy(CIMultiDict(headers or resp_headers))
    resp._raw_headers = tuple(
        (k.encode(), v.encode()) for k, v in resp._headers.items()
    )

    fake_body: bytes = make_response_body(url)

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
    req.url = req_url + "/get"
    req.headers = CaseInsensitiveDict(req_headers)
    #req.body = b'{"key": "value"}'
    return req


@pytest.fixture
def sync_response() -> Response:
    url: str = req_url + "/get"
    
    resp = Response()
    resp.url = url
    resp.status_code = 200
    resp.reason = "OK"
    resp.headers = CaseInsensitiveDict(resp_headers)
    resp._content = make_response_body(url)
    return resp


@pytest_asyncio.fixture
async def async_request() -> ClientRequest:
    headers: CIMultiDict[str] = CIMultiDict(req_headers)
    url = URL(req_url + "/get")
    req = ClientRequest(method="GET", url=url, headers=headers)
    #req.update_body_from_data(json.dumps({"key": "value"}).encode())
    return req


@pytest_asyncio.fixture
async def async_response() -> ClientResponse:
    url: str = req_url + "/get"

    request_info: RequestInfo = make_request(url)
    return make_response(
        method="GET",
        url=url,
        status=200,
        reason="OK",
        request_info=request_info,
    )


@pytest_asyncio.fixture
async def async_redirected_response(async_response: ClientResponse) -> ClientResponse:
    url: str = req_url + "/redirect/1"

    request_info: RequestInfo = make_request(url)
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

    final_resp: ClientResponse = async_response
    final_resp._history = (resp,)

    return final_resp
