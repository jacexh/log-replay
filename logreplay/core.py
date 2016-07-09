import asyncio
import timeit
from asyncio import Queue
import random
import logging
import aiohttp
from . import events
from . import config
from .model import RequestInfo


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
            for _ in range(int(round((config.PLAYER_NUMBER/config.REPEATER_NUMBER)+0.5))):
                REPLAY_QUEUE.put_nowait(request_info)  # notify the player to finish
            LOGGER.info("repeat finished")
            break

        if not isinstance(request_info, RequestInfo):
            LOGGER.error("incorrect message in repeat queue: {}".format(request_info))
            continue

        while replay_rate > 0:
            if replay_rate >= 1:
                parameters = request_info.to_request_parameters()
                events.repeat.fire(parameters=parameters)  # do not unpack parameters
                REPLAY_QUEUE.put_nowait(parameters)
            else:
                r = random.random()
                if r <= rate:
                    parameters = request_info.to_request_parameters()
                    events.repeat.fire(parameters=parameters)  # do not unpack parameters
                    REPLAY_QUEUE.put_nowait(parameters)
            replay_rate -= 1


async def request(method, url, **kwargs):
    """http请求函数

    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    future = asyncio.Future()
    if config.CALLBACK:
        future.add_done_callback(config.CALLBACK)

    start = timeit.default_timer()
    async with CLIENT.request(method, url, **kwargs) as response:
        content = await response.text()
        result = dict(
            request=kwargs,
            response=dict(
                status_code=response.status,
                content=content,
                latency=int((timeit.default_timer()-start)*1000),
                method=response.method,
                url=response.url,
                headers=response.headers,
                cookies=response.cookies
            ))
        if config.CALLBACK:
            future.set_result(result)


async def player():
    """请求发送器

    :param q:
    :return:
    """
    while 1:
        parameters = await REPLAY_QUEUE.get()
        if parameters == config.FINISHED_SIGNAL:
            LOGGER.info("player finished")
            break

        events.replay.fire(parameters=parameters)

        method = parameters.pop('method', 'get')
        url = parameters.pop('url', None)
        params = parameters.pop('params', None)
        data = parameters.pop('data', None)
        headers = parameters.pop('headers', None)
        try:
            await request(method, url, params=params, data=data, headers=headers, **parameters)
        except:
            pass
