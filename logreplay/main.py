import os
import asyncio
from logreplay import config
from logreplay.core import EVENT_LOOP, REPEAT_QUEUE, REPLAY_QUEUE, player, repeater
from logreplay.parser import ParserThread
from concurrent.futures import ThreadPoolExecutor


def main(log_file=None, rate=1, log_parser=None):
    """
    logreplay主函数
    :param log_file: 日志文件
    :param rate: 默认原速回; 当>1时, 比如2,从日志中读取到的一条http请求,将会被并发请求两次; 当0<rate<1时,如0.5,该http请求,有50%的概率不回放
    :param log_parser: 日志解析器
    :return:
    """

    if not os.path.isfile(log_file):
        raise IOError("cannot find log file: {}".format(log_file))

    ParserThread(log_file, log_parser).start()

    [asyncio.ensure_future(repeater(REPEAT_QUEUE, REPLAY_QUEUE, rate)) for _ in range(config.REPEATER_NUMBER)]
    [asyncio.ensure_future(player(REPLAY_QUEUE)) for _ in range(config.PLAYER_NUMBER)]

    EVENT_LOOP.set_default_executor(ThreadPoolExecutor(config.THREAD_POOL_NUMBER))
    EVENT_LOOP.run_forever()
