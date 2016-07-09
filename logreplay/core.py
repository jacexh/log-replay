import asyncio
from asyncio import Queue
import aiohttp
import random
import logging
from . import events
from . import config
from .parser import RequestInfo
import timeit


EVENT_LOOP = asyncio.get_event_loop()
REPLAY_QUEUE = Queue(loop=EVENT_LOOP)  # 回放队列,生产者为中继器,消费者将会生成的异步请求
REPEAT_QUEUE = Queue(loop=EVENT_LOOP)  # 中继队列,消费者为中继器,用于更改请求量
CLIENT = aiohttp.ClientSession(loop=EVENT_LOOP)
LOGGER = logging.getLogger(__name__)


async def repeater(rate):
    """中继器

    :param rate:
    :return:
    """
    while 1:
        request_info = await REPEAT_QUEUE.get()
        replay_rate = rate

        if request_info == config.FINISHED_SIGNAL:
            REPEAT_QUEUE.put_nowait(request_info)  # notify the player to finish
            LOGGER.info("repeat finished")
            break

        if not isinstance(request_info, RequestInfo):
            continue

        while replay_rate > 0:
            if replay_rate >= 1:
                parameters = request_info.to_request_parameters()
                events.repeat.fire(parameters=parameters)  # do not unpack parameters
                REPEAT_QUEUE.put_nowait(parameters)
            else:
                r = random.random()
                if r <= rate:
                    parameters = request_info.to_request_parameters()
                    events.repeat.fire(parameters=parameters)  # do not unpack parameters
                    REPEAT_QUEUE.put_nowait(parameters)
            replay_rate -= 1


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
            request=dict(
                url=url,
                method=method,
                parameters=kwargs
            ),
            response=dict(
                status_code=response.status,
                content=content,
                elapsed=timeit.default_timer()-start,
                host=response.host,
                method=response.method,
                url=response.url,
                cookies=response.cookies
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
