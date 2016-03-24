import os
import asyncio
from .config import config
from .core import EVENT_LOOP, REPEAT_QUEUE, REPLAY_QUEUE, player, repeater, EXECUTOR
from .parser import ParserThread
from .monitor import MonitorThread


def main(log_file, log_parser, rate=1, file_encoding="utf-8"):
    """
    logreplay主函数
    :param log_file: 日志文件
    :param rate: 默认原速回; 当>1时, 比如2,从日志中读取到的一条http请求,将会被并发请求两次; 当0<rate<1时,如0.5,该http请求,有50%的概率不回放
    :param log_parser: 日志解析器
    :param file_encoding:
    :return:
    """

    if not os.path.isfile(log_file):
        raise IOError("cannot find log file: {}".format(log_file))

    pt = ParserThread(log_file, log_parser, file_encoding=file_encoding)
    pt.start()
    MonitorThread(pt).start()

    [asyncio.ensure_future(repeater(REPEAT_QUEUE, REPLAY_QUEUE, rate)) for _ in range(config.REPEATER_NUMBER)]
    [asyncio.ensure_future(player(REPLAY_QUEUE)) for _ in range(config.PLAYER_NUMBER)]

    EVENT_LOOP.set_default_executor(EXECUTOR)
    EVENT_LOOP.run_forever()
