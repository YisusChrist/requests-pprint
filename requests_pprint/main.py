import json

from requests.models import PreparedRequest, Response
from aiohttp import ClientRequest, ClientResponse, RequestInfo

try:
    from rich import print  # pylint: disable=redefined-builtin  # pip install rich
except ImportError:
    pass


async def pprint_async_http_request(req: ClientRequest | RequestInfo) -> None:
    """
    Pretty print an aiohttp ClientRequest.

    Args:
        req (aiohttp.ClientRequest): The request to print.
    """
    if not req:
        return

    if "Host" not in req.headers and req.url:
        req.headers["Host"] = req.url.host  # type: ignore

    path: str = req.url.path_qs or "/"

    http_version = "HTTP/1.1"

    if isinstance(req, RequestInfo):
        body: str = ""
    else:
        if isinstance(req.body, bytes):
            body = req.body.decode()
        else:
            body = req.body or ""

    msg: str = "{}\n{}\r\n{}\r\n\r\n{}\n{}".format(
        "--------------START--------------",
        f"{req.method} {path} {http_version}",
        "\r\n".join(f"[b]{k}[/]: {v}" for k, v in req.headers.items()),
        body,
        "---------------END---------------",
    )

    print(msg)


async def pprint_async_http_response(resp: ClientResponse) -> None:
    """
    Pretty print an aiohttp ClientResponse.

    Args:
        resp (aiohttp.ClientResponse): The response to print.
    """
    if not resp:
        return

    http_version: str = "HTTP/1.1"
    response_body: str = await resp.text()

    try:
        response_body = json.dumps(json.loads(response_body), indent=2)
    except json.decoder.JSONDecodeError:
        pass

    msg: str = "{}\n{}\r\n{}\r\n\r\n{}\n{}".format(
        "--------------START--------------",
        f"{http_version} {resp.status} {resp.reason}",
        "\r\n".join(f"[b]{k}[/]: {v}" for k, v in resp.headers.items()),
        response_body,
        "---------------END---------------",
    )

    print(msg)


async def print_async_response_summary(response: ClientResponse) -> None:
    """
    Print a summary of the response.

    Args:
        response (aiohttp.ClientResponse): The response to print.
    """
    if not response:
        return

    if response.history:
        print("[bold yellow]Request was redirected![/]")
        print("------ ORIGINAL REQUEST ------")
        await pprint_async_http_request(response.history[0].request_info)
        print("------ ORIGINAL RESPONSE ------")
        await pprint_async_http_response(response.history[0])
        print("------ REDIRECTED REQUEST ------")
        await pprint_async_http_request(response.request_info)
        print("------ REDIRECTED RESPONSE ------")
        await pprint_async_http_response(response)
    else:
        print("[bold green]Request was not redirected[/]")
        await pprint_async_http_request(response.request_info)
        await pprint_async_http_response(response)


def pprint_http_request(req: PreparedRequest) -> None:
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
        body = req.body or ""

    msg: str = "{}\n{}\r\n{}\r\n\r\n{}\n{}".format(
        "--------------START--------------",
        f"{req.method} {path} {http_version}",
        "\r\n".join(f"[b]{k}[/]: {v}" for k, v in req.headers.items()),
        body,
        "---------------END---------------",
    )

    print(msg)


def pprint_http_response(resp: Response) -> None:
    """
    At this point it is completely built and ready
    to be fired; it is "prepared".

    However pay attention at the formatting used in
    this function because it is programmed to be pretty
    printed and may differ from the actual request.

    Args:
        resp (requests.models.Response): The response to print.
    """
    if not resp:
        return

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


def print_response_summary(response: Response) -> None:
    """
    Print a summary of the response.

    Args:
        response (requests.models.Response): The response to print.
    """
    if not response:
        return

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
