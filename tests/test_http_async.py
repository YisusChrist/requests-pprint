import pytest
from _pytest.capture import CaptureResult
from aiohttp import ClientRequest, ClientResponse, ClientSession

from requests_pprint import (pprint_async_http_request,
                             pprint_async_http_response,
                             print_async_response_summary)


@pytest.mark.asyncio
async def test_pprint_async_http_request(
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
async def test_pprint_async_http_response(
    async_sample_response: ClientResponse, capsys: pytest.CaptureFixture[str]
) -> None:
    await pprint_async_http_response(async_sample_response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "--------------START--------------" in captured.out
    assert "HTTP/1.1 200 OK" in captured.out
    assert "Content-Type: application/json" in captured.out
    assert '"url": "https://httpbin.org/get"' in captured.out
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
    aitohttp_client: ClientSession, capsys: pytest.CaptureFixture[str]
) -> None:
    # Simulate a redirected response
    response: ClientResponse = await aitohttp_client.get(
        "https://httpbin.org/redirect/1"
    )
    await print_async_response_summary(response)
    captured: CaptureResult[str] = capsys.readouterr()

    assert "Request was redirected!" in captured.out
    assert "------ ORIGINAL REQUEST ------" in captured.out
    assert "------ ORIGINAL RESPONSE ------" in captured.out
    assert "------ REDIRECTED REQUEST ------" in captured.out
    assert "------ REDIRECTED RESPONSE ------" in captured.out
