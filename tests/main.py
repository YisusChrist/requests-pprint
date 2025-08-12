import asyncio
import contextlib
import time

import requests
from aiohttp import ClientSession
from rich import print
from rich.traceback import install

from requests_pprint import print_async_response_summary
from requests_pprint.http_sync import print_response_summary

headers: dict[str, str] = {"Custom-Header": "CustomValue"}
payload: dict[str, str] = {"key1": "value1", "key2": "value2"}


async def send_get_requests(session: ClientSession, url: str) -> None:
    print("# 1. ASYNC WITH")
    async with session.get(url, headers=headers, params=payload) as response:
        await print_async_response_summary(response)

    print("# 2. ASYNC DIRECT")
    response = await session.get(url, headers=headers, params=payload)
    await print_async_response_summary(response)

    print("# 3. SYNC")
    response = requests.get(url, headers=headers, params=payload)
    print_response_summary(response)


async def send_post_requests(session: ClientSession, url: str) -> None:
    print("# 1. ASYNC WITH")
    async with session.post(url, data=payload) as response:
        await print_async_response_summary(response)

    print("# 2. ASYNC DIRECT")
    response = await session.post(url, data=payload)
    await print_async_response_summary(response)

    print("# 3. SYNC")
    response = requests.post(url, data=payload)
    print_response_summary(response)


async def send_redirect_requests(session: ClientSession, url: str) -> None:
    print("# 1. ASYNC WITH")
    async with session.get(url) as response:
        await print_async_response_summary(response)

    print("# 2. ASYNC DIRECT")
    response = await session.get(url)
    await print_async_response_summary(response)

    print("# 3. SYNC")
    response = requests.get(url)
    print_response_summary(response)


async def send_media_requests(session: ClientSession, url: str) -> None:
    print("# 1. ASYNC WITH")
    start_time: float = time.time()
    async with session.get(url) as response:
        with contextlib.redirect_stdout(None):
            await print_async_response_summary(response)
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

    print("# 2. SYNC DIRECT")
    start_time = time.time()
    response = await session.get(url)
    with contextlib.redirect_stdout(None):
        await print_async_response_summary(response)
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

    print("# 3. SYNC")
    start_time = time.time()
    response = requests.get(url, stream=True)
    with contextlib.redirect_stdout(None):
        print_response_summary(response)
    print(f"Time taken: {time.time() - start_time:.2f} seconds")


async def main() -> None:
    install()

    async with ClientSession() as session:
        get_url = "https://httpbin.org/get"
        post_url = "https://httpbin.org/post"
        redirect_url = "https://httpbin.org/redirect/1"
        image_url = "https://images.pexels.com/photos/459225/pexels-photo-459225.jpeg?cs=srgb&dl=daylight-environment-forest-459225.jpg"
        video_url = "https://ia903407.us.archive.org/0/items/big-bunny-sample-video/SampleVideo.mp4"
        large_video_url = "https://dn720406.ca.archive.org/0/items/sample-video-file-100-mb/Sample_Video_File_100MB.mp4"

        await send_get_requests(session, get_url)
        await send_post_requests(session, post_url)
        await send_redirect_requests(session, redirect_url)
        await send_media_requests(session, image_url)
        await send_media_requests(session, video_url)
        await send_media_requests(session, large_video_url)


if __name__ == "__main__":
    asyncio.run(main())
