import pytest
from _pytest.capture import CaptureResult
from requests.models import PreparedRequest, Response

from requests_pprint import (pprint_http_request, pprint_http_response,
                             print_response_summary)


def test_pprint_http_request(
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


def test_pprint_http_response(
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
