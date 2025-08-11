def assert_missing_host_output(output: str) -> None:
    assert "Host: mytest.com" in output
    assert "GET /path HTTP/1.1" in output


def assert_binary_body_output(output: str) -> None:
    assert "[BINARY DATA]" in output


def assert_full_request_output(output: str) -> None:
    assert "--------------START--------------" in output
    assert "GET /get HTTP/1.1" in output
    assert "User-Agent: Python/3.9 aiohttp/3.12.15" in output
    assert "Accept-Encoding: gzip, deflate" in output
    assert "Accept: */*" in output
    assert "Host: httpbin.org" in output
    assert "---------------END---------------" in output


def assert_full_response_output(output: str) -> None:
    assert "--------------START--------------" in output
    assert "HTTP/1.1 200 OK" in output
    assert "Date: Mon, 11 Aug 2025 10:13:53 GMT" in output
    assert "Content-Type: application/json" in output
    assert "Content-Length: 418" in output
    assert "Connection: keep-alive" in output
    assert "Server: gunicorn/19.9.0" in output
    assert "Access-Control-Allow-Origin: *" in output
    assert "Access-Control-Allow-Credentials: true" in output
    assert '"url": "https://httpbin.org/get"' in output
    assert "---------------END---------------" in output


def assert_no_redirect_output(output: str) -> None:
    assert "Request was not redirected" in output


def assert_redirect_output(output: str) -> None:
    assert "Request was redirected!" in output
    assert "------ ORIGINAL REQUEST ------" in output
    assert "------ ORIGINAL RESPONSE ------" in output
    assert "------ REDIRECTED REQUEST ------" in output
    assert "------ REDIRECTED RESPONSE ------" in output
