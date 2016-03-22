import asyncio
import aiohttp
import random


EVENT_LOOP = asyncio.get_event_loop()
REPLAY_QUEUE = asyncio.Queue()  # 回放队列,生产者为中继器,消费者将会生成的异步请求
REPEAT_QUEUE = asyncio.Queue()  # 中继队列,消费者为中继器,用于更改请求量
CLIENT = aiohttp.ClientSession(loop=EVENT_LOOP)


async def repeater(repeat_q, replay_q, rate):
    """

    :param repeat_q:
    :param replay_q:
    :param rate:
    :return:
    """
    while 1:
        params = await repeat_q.get()
        loop_rate = rate
        while loop_rate > 0:
            if loop_rate >= 1:
                replay_q.put_nowait(params)
            else:
                r = random.random()
                if r <= rate:
                    replay_q.put_nowait(params)
            loop_rate -= 1


async def request(method, url, **kwargs):
    """
    http请求函数
    :param method:
    :param url:
    :param kwargs:
    :return:
    """
    session = kwargs.pop('client', None)
    if session is None:
        global CLIENT
        session = CLIENT
    async with session.request(method, url) as response:
        return await response.read()


async def player(q):
    """
    请求发送器
    :param q:
    :return:
    """
    global EVENT_LOOP
    client = aiohttp.ClientSession(loop=EVENT_LOOP)
    while 1:
        url = await q.get()
        await request('get', url, client=client)
