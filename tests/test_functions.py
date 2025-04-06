import json

import pytest
import pytest_asyncio
from _pytest.capture import CaptureResult
from aiohttp import ClientRequest, ClientResponse, ClientSession
from multidict import CIMultiDict
from requests.models import PreparedRequest, Response
from requests.structures import CaseInsensitiveDict
from yarl import URL

from requests_pprint import (pprint_async_http_request,
                             pprint_async_http_response, pprint_http_request,
                             pprint_http_response,
                             print_async_response_summary,
                             print_response_summary)


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
    async with aitohttp_client.get("https://example.com") as response:
        return response


def test_pretty_print_http_request(
    sample_request: PreparedRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    pprint_http_request(sample_request)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "--------------START--------------" in captured.out
    assert "GET / HTTP/1.1" or "GET  HTTP/1.1" in captured.out
    assert "User-Agent: Mozilla/5.0" in captured.out
    assert "Host: example.com" in captured.out
    assert '{"key": "value"}' in captured.out
    assert "---------------END---------------" in captured.out


def test_pretty_print_http_response(
    sample_response: Response, capsys: pytest.CaptureFixture[str]
) -> None:
    pprint_http_response(sample_response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "--------------START--------------" in captured.out
    assert "HTTP/1.1 200 OK" in captured.out
    assert "Content-Type: application/json" in captured.out
    assert '"status": "success"' in captured.out
    assert "---------------END---------------" in captured.out


def test_print_response_summary_no_redirect(
    sample_response: Response, capsys: pytest.CaptureFixture[str]
) -> None:
    sample_response.history = []  # Simulate no redirect
    print_response_summary(sample_response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "Request was not redirected" in captured.out


def test_print_response_summary_redirect(
    sample_response: Response, capsys: pytest.CaptureFixture[str]
) -> None:
    # Simulate a redirected response
    sample_response.history = [sample_response]
    print_response_summary(sample_response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "Request was redirected!" in captured.out
    assert "------ ORIGINAL REQUEST ------" in captured.out
    assert "------ ORIGINAL RESPONSE ------" in captured.out
    assert "------ REDIRECTED REQUEST ------" in captured.out
    assert "------ REDIRECTED RESPONSE ------" in captured.out


@pytest.mark.asyncio
async def test_pretty_print_async_http_request(
    async_sample_request: ClientRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    await pprint_async_http_request(async_sample_request)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "--------------START--------------" in captured.out
    assert "GET / HTTP/1.1" in captured.out
    assert "User-Agent: Mozilla/5.0" in captured.out
    assert "Host: example.com" in captured.out
    assert "---------------END---------------" in captured.out


@pytest.mark.asyncio
async def test_pretty_print_async_http_response(
    async_sample_response: ClientResponse, capsys: pytest.CaptureFixture[str]
) -> None:
    await pprint_async_http_response(async_sample_response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "--------------START--------------" in captured.out
    assert "HTTP/1.1 200 OK" in captured.out
    assert "Content-Type: application/json" in captured.out
    assert '"status": "success"' in captured.out
    assert "---------------END---------------" in captured.out


@pytest.mark.asyncio
async def test_print_async_response_summary_no_redirect(
    async_sample_response: ClientResponse, capsys: pytest.CaptureFixture[str]
) -> None:
    await print_async_response_summary(async_sample_response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "Request was not redirected" in captured.out


@pytest.mark.asyncio
async def test_print_async_response_summary_redirect(
    async_sample_response: ClientResponse, capsys: pytest.CaptureFixture[str]
) -> None:
    # Simulate a redirected response
    #async_sample_response.history
    await print_async_response_summary(async_sample_response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "Request was redirected!" in captured.out
    assert "------ ORIGINAL REQUEST ------" in captured.out
    assert "------ ORIGINAL RESPONSE ------" in captured.out
    assert "------ REDIRECTED REQUEST ------" in captured.out
    assert "------ REDIRECTED RESPONSE ------" in captured.out
