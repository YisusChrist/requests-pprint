from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from yarl import URL

from requests_pprint import (pprint_async_http_request,
                             pprint_async_http_response,
                             print_async_response_summary)
from tests._assert_helpers import *

if TYPE_CHECKING:
    from _pytest.capture import CaptureResult
    from aiohttp import ClientRequest, ClientResponse


@pytest.mark.asyncio
async def test_pprint_async_http_request_none() -> None:
    with pytest.raises(AttributeError) as e:
        await pprint_async_http_request(None)
    assert "'NoneType' object has no attribute 'headers'" in str(e.value)

@pytest.mark.asyncio
async def test_pprint_async_http_request_missing_host(
    async_request: ClientRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    async_request.headers.pop("User-Agent", None)
    async_request.headers.pop("Host", None)
    async_request.url = URL("https://mytest.com/path")
    await pprint_async_http_request(async_request)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_missing_host_output(captured.out)


@pytest.mark.asyncio
async def test_pprint_async_http_request_binary_body(
    async_request: ClientRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    async_request.headers["Content-Type"] = "application/pdf"
    async_request.body = b"%PDF-1.4..."
    await pprint_async_http_request(async_request)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_binary_body_output(captured.out)


@pytest.mark.asyncio
async def test_pprint_async_http_request(
    async_request: ClientRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    await pprint_async_http_request(async_request)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_full_request_output(captured.out)


@pytest.mark.asyncio
async def test_pprint_async_http_response(
    async_response: ClientResponse, capsys: pytest.CaptureFixture[str]
) -> None:
    await pprint_async_http_response(async_response)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_full_response_output(captured.out)


@pytest.mark.asyncio
async def test_print_async_response_summary_no_redirect(
    async_response: ClientResponse, capsys: pytest.CaptureFixture[str]
) -> None:
    await print_async_response_summary(async_response)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_no_redirect_output(captured.out)


@pytest.mark.asyncio
async def test_print_async_response_summary_redirect(
    async_redirected_response: ClientResponse, capsys: pytest.CaptureFixture[str]
) -> None:
    await print_async_response_summary(async_redirected_response)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_redirect_output(captured.out)
