import time
import asyncio
import threading
import logging
from abc import abstractmethod, ABCMeta
from . import config
from .core import REPEAT_QUEUE


class LogParser(metaclass=ABCMeta):

    @abstractmethod
    def parse(self, line):
        """Implement the method in subclass and return an instance of RequestInfo

        :param line: one line in log file
        :type line: str
        :return: an instance of RequestInfo
        """
        pass


class ParserThread(threading.Thread):

    def __init__(self, log_file, log_parser, file_encoding='utf-8'):
        super(ParserThread, self).__init__()
        if not issubclass(log_parser, LogParser):
            raise TypeError
        self.log_file = log_file
        self.log_parser = log_parser()
        self.logger = logging.getLogger(__name__)
        self.file_encoding = file_encoding
        self.loop = asyncio.get_event_loop()

    def run(self):
        last_gather_ts = None
        diff_ts = None  # 回放时间与原记录时间差
        matched_records_in_cycle = 0

        with open(self.log_file, "r", encoding=self.file_encoding) as f:
            for line in f.readlines():
                request_info = self.log_parser.parse(line)
                if not request_info.is_matched:  # 当该行并非请求日志时,不处理
                    continue

                if config.GATHER_INTERVAL == 0:  # 不控制采集间隔的情况下, 不会控制回放的节奏
                    self.logger.debug(request_info)
                    self.loop.call_soon_threadsafe(REPEAT_QUEUE.put_nowait, request_info)
                else:
                    if request_info.timestamp is None:
                        raise ValueError("if set GATHER_INTERVAL not eq 0, must specify the `timestamp` "
                                         "in the instance of `RequestInfo`")
                    if last_gather_ts is None:  # 取到第一条匹配的请求日志, 回放开始
                        last_gather_ts = request_info.timestamp
                        diff_ts = int(time.time() * 1000) - last_gather_ts
                        matched_records_in_cycle += 1
                        self.logger.debug(request_info)
                        self.loop.call_soon_threadsafe(REPEAT_QUEUE.put_nowait, request_info)
                        continue

                    if request_info.timestamp - last_gather_ts <= config.GATHER_INTERVAL * 1000:
                        self.logger.debug(request_info)
                        matched_records_in_cycle += 1
                        self.loop.call_soon_threadsafe(REPEAT_QUEUE.put_nowait, request_info)
                    else:
                        while 1:
                            self.logger.info("gathered {} records in {} seconds".format(
                                matched_records_in_cycle, config.GATHER_INTERVAL))
                            time.sleep(config.GATHER_INTERVAL)
                            last_gather_ts = int(time.time()*1000) - diff_ts
                            matched_records_in_cycle = 0

                            if request_info.timestamp - last_gather_ts < config.GATHER_INTERVAL * 1000:
                                matched_records_in_cycle += 1
                                self.logger.debug(request_info)
                                self.loop.call_soon_threadsafe(REPEAT_QUEUE.put_nowait, request_info)
                                break

        self.logger.info("read complete")
