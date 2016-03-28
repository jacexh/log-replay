import asyncio
import aiohttp
import random
import logging
import janus
from .config import config
from concurrent.futures import ThreadPoolExecutor
import timeit


EVENT_LOOP = asyncio.get_event_loop()
REPLAY_QUEUE = janus.Queue(loop=EVENT_LOOP)  # 回放队列,生产者为中继器,消费者将会生成的异步请求
REPEAT_QUEUE = janus.Queue(loop=EVENT_LOOP)  # 中继队列,消费者为中继器,用于更改请求量
EXECUTOR = ThreadPoolExecutor(config.THREAD_POOL_NUMBER)
CLIENT = aiohttp.ClientSession(loop=EVENT_LOOP)
LOGGER = logging.getLogger(__name__)


async def repeater(repeat_q, replay_q, rate):
    """
    中继器
    :param repeat_q:
    :param replay_q:
    :param rate:
    :return:
    """
    while 1:
        parameters = await repeat_q.async_q.get()
        loop = rate
        while loop > 0:
            if loop >= 1:
                replay_q.async_q.put_nowait(parameters.copy())
            else:
                r = random.random()
                if r <= rate:
                    replay_q.async_q.put_nowait(parameters.copy())
            loop -= 1


async def request(client, method, url, **kwargs):
    """
    http请求函数
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    if config.RESPONSE_HANDLER is not None:
        future = asyncio.Future()
        future.add_done_callback(config.RESPONSE_HANDLER)
    start = timeit.default_timer()
    async with client.request(method, url, **kwargs) as response:
        content = await response.text()
        r = dict(
            request=dict(url=url, method=method, paramenters=kwargs),
            response=dict(
                status_code=response.status,
                content=content,
                elapsed=timeit.default_timer()-start,
                host=response.host,
                method=response.method,
                url=response.url,
                cokkies=response.cookies
            ))
        if config.RESPONSE_HANDLER is not None:
            future.set_result(r)


async def player(q):
    """
    请求发送器
    :param q:
    :return:
    """
    while 1:
        parameters = await q.async_q.get()
        method = parameters.pop('method', 'get')
        url = parameters.pop('url')
        params = parameters.pop('param', None)
        data = parameters.pop('body', None)
        headers = parameters.pop('headers', None)
        await request(CLIENT, method, url, params=params, data=data, headers=headers, **parameters)
