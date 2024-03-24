import json

import requests  # pip install requests

try:
    from rich import print  # pylint: disable=redefined-builtin  # pip install rich
except ImportError:
    pass


def pprint_http_request(req: requests.models.PreparedRequest) -> None:
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.

    Reference: https://stackoverflow.com/a/23816211/19705722

    Args:
        req (requests.models.PreparedRequest): The request to print.
    """
    if not req:
        return

    if "Host" not in req.headers and req.url:
        req.headers["Host"] = req.url.split("/")[2]

    if req.url:
        path: str = req.url.split(req.headers["Host"])[-1]
    else:
        path = req.path_url

    if not path:
        path = "/"

    http_version: str = "HTTP/1.1"
    if isinstance(req.body, bytes):
        body: str = req.body.decode()
    else:
        body = str(req.body)

    msg: str = "{}\n{}\r\n{}\r\n\r\n{}\n{}".format(
        "--------------START--------------",
        f"{req.method} {path} {http_version}",
        "\r\n".join(f"[b]{k}[/]: {v}" for k, v in req.headers.items()),
        body or "",
        "---------------END---------------",
    )

    print(msg)


def pprint_http_response(resp: requests.models.Response) -> None:
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.

    Args:
        resp (requests.models.Response): The response to print.
    """
    if not resp.raw:
        http_version = "HTTP/1.1"
    else:
        http_version = f"HTTP/{resp.raw.version // 10}.{resp.raw.version % 10}"

    try:
        response_body: str = json.dumps(json.loads(resp.text), indent=2)
    except json.decoder.JSONDecodeError:
        response_body = resp.text or resp.content.decode()

    msg: str = "{}\n{}\r\n{}\r\n\r\n{}\n{}".format(
        "--------------START--------------",
        f"{http_version} {resp.status_code} {resp.reason}",
        "\r\n".join(f"[b]{k}[/]: {v}" for k, v in resp.headers.items()),
        response_body,
        "---------------END---------------",
    )

    print(msg)


def print_response_summary(response: requests.models.Response) -> None:
    """
    Print a summary of the response.

    Args:
        response (requests.models.Response): The response to print.
    """
    if response.history:
        print("[bold yellow]Request was redirected![/]")
        print("------ ORIGINAL REQUEST ------")
        pprint_http_request(response.history[0].request)
        print("------ ORIGINAL RESPONSE ------")
        pprint_http_response(response.history[0])
        print("------ REDIRECTED REQUEST ------")
        pprint_http_request(response.request)
        print("------ REDIRECTED RESPONSE ------")
        pprint_http_response(response)
    else:
        print("[bold green]Request was not redirected[/]")
        pprint_http_request(response.request)
        pprint_http_response(response)
