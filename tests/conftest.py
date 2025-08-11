import json

import pytest
import pytest_asyncio
from aiohttp import ClientRequest, ClientResponse, ClientSession
from multidict import CIMultiDict
from requests.models import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict
from yarl import URL


@pytest.fixture
def sample_request() -> PreparedRequest:
    req = PreparedRequest()
    req.method = "GET"
    req.url = "https://example.com"
    req.headers = CaseInsensitiveDict({"User-Agent": "Mozilla/5.0"})
    req.body = b'{"key": "value"}'
    return req


@pytest.fixture
def sample_response() -> Response:
    resp = Response()
    resp.status_code = 200
    resp.reason = "OK"
    resp.headers = CaseInsensitiveDict({"Content-Type": "application/json"})
    resp._content = b'{"status": "success"}'
    return resp


@pytest_asyncio.fixture
async def async_sample_request() -> ClientRequest:
    headers = CIMultiDict({"User-Agent": "Mozilla/5.0"})
    url = URL("https://example.com")
    req = ClientRequest(method="GET", url=url, headers=headers)
    req.update_body_from_data(json.dumps({"key": "value"}).encode())
    return req


@pytest_asyncio.fixture
async def aitohttp_client() -> ClientSession:
    return ClientSession(raise_for_status=True)


@pytest_asyncio.fixture
async def async_sample_response(aitohttp_client: ClientSession) -> ClientResponse:
    return await aitohttp_client.get("https://httpbin.org/get")
