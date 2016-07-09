import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from . import config
from .core import REPLAY_QUEUE, player, repeater
from .parser import ParserThread
from .monitor import MonitorThread


def main(log_file, log_parser, rate=1, file_encoding="utf-8", callback=None):
    """log replay主函数

    :param log_file: log file path
    :param rate: 默认原速回; 当>1时, 比如2,从日志中读取到的一条http请求,将会被并发请求两次; 当0<rate<1时,如0.5,该http请求,有50%的概率不回放
    :param log_parser: 日志解析器
    :param file_encoding: 日志文件编码
    :param callback: 回调函数
    :return:
    """

    if not os.path.isfile(log_file):
        raise IOError("cannot find log file: {}".format(log_file))

    if callback is not None:
        config.RESPONSE_HANDLER = callback

    pt = ParserThread(log_file, log_parser, file_encoding=file_encoding)
    pt.start()
    MonitorThread(pt).start()

    [asyncio.ensure_future(repeater(rate)) for _ in range(config.REPEATER_NUMBER)]
    [asyncio.ensure_future(player(REPLAY_QUEUE)) for _ in range(config.PLAYER_NUMBER)]

    event_loop = asyncio.get_event_loop()
    event_loop.set_default_executor(ThreadPoolExecutor(config.THREAD_POOL_NUMBER))
    event_loop.run_forever()
    event_loop.close()
