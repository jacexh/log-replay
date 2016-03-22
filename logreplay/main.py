import os
import asyncio
from logreplay import config
from logreplay.core import EVENT_LOOP, REPEAT_QUEUE, REPLAY_QUEUE, player, repeater
from concurrent.futures import ThreadPoolExecutor


def main(log_file=None, rate=1, log_cutter=None, request_parser=None):
    """
    logreplay主函数
    :param log_file: 日志文件
    :param rate: 默认原速回; 当>1时, 比如2,从日志中读取到的一条http请求,将会被并发请求两次; 当0<rate<1时,如0.5,该http请求,有50%的概率不回放
    :param log_cutter: 日志切割器
    :param request_parser: 请求解析器
    :return:
    """

    # if not os.path.isfile(log_file):
    #     raise IOError("cannot find log file: {}".format(log_file))
    rate = 3

    [asyncio.ensure_future(repeater(REPEAT_QUEUE, REPLAY_QUEUE, 3)) for i in range(config.REPEATER_NUMBER)]

    for x in range(config.PLAYER_NUMBER):
        asyncio.ensure_future(player(REPLAY_QUEUE))
    EVENT_LOOP.set_default_executor(ThreadPoolExecutor(5))
    EVENT_LOOP.run_forever()


if __name__ == "__main__":
    for _ in range(5):
        REPEAT_QUEUE.put_nowait("http://127.0.0.1:5000/ping")
    main()
