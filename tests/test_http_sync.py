from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from requests_pprint import (pprint_http_request, pprint_http_response,
                             print_response_summary)
from tests._assert_helpers import *

if TYPE_CHECKING:
    from _pytest.capture import CaptureResult
    from requests.models import PreparedRequest, Response


def test_pprint_http_request_none(capsys: pytest.CaptureFixture[str]) -> None:
    pprint_http_request(None)
    captured: CaptureResult[str] = capsys.readouterr()
    assert captured.out == ""


def test_pprint_http_request_missing_host(
    sync_request: PreparedRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    sync_request.headers.pop("User-Agent", None)
    sync_request.headers.pop("Host", None)
    sync_request.url = "https://mytest.com/path"
    pprint_http_request(sync_request)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_missing_host_output(captured.out)


def test_pprint_http_request_binary_body(
    sync_request: PreparedRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    sync_request.headers["Content-Type"] = "application/pdf"
    sync_request.body = b"%PDF-1.4..."
    pprint_http_request(sync_request)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_binary_body_output(captured.out)


def test_pprint_http_request(
    sync_request: PreparedRequest, capsys: pytest.CaptureFixture[str]
) -> None:
    pprint_http_request(sync_request)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_full_request_output(captured.out)


def test_pprint_http_response(
    sync_response: Response, capsys: pytest.CaptureFixture[str]
) -> None:
    pprint_http_response(sync_response)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_full_response_output(captured.out)


def test_print_response_summary_no_redirect(
    sync_response: Response, capsys: pytest.CaptureFixture[str]
) -> None:
    sync_response.history = []  # Simulate no redirect
    print_response_summary(sync_response)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_no_redirect_output(captured.out)


def test_print_response_summary_redirect(
    sync_response: Response, capsys: pytest.CaptureFixture[str]
) -> None:
    # Simulate a redirected response
    sync_response.history = [sync_response]
    print_response_summary(sync_response)
    captured: CaptureResult[str] = capsys.readouterr()
    assert_redirect_output(captured.out)
