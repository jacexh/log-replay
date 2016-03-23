import time
import threading
import logging
from .config import GATHER_INTERVAL
from .core import REPEAT_QUEUE


class LogParser(object):

    request_url = None
    request_method = "get"
    request_headers = None
    request_body = None
    request_start_timestamp = None  # unix时间戳,毫秒级
    is_matched = False

    def __init__(self, content):
        self.content = content

    def parse(self):
        """
        子类须实现该方法,如果记录匹配,必须修改is_matched为True
        :return:
        """
        pass

    def obj_to_dict(self):
        if self.is_matched:
            return dict(
                url=self.request_url, method=self.request_method, body=self.request_body, headers=self.request_headers)
        return {}


class ParserThread(threading.Thread):

    def __init__(self, log_file, log_parser, file_encoding='utf-8'):
        super(ParserThread, self).__init__()
        if not issubclass(log_parser, LogParser):
            raise TypeError
        self.log_file = log_file
        self.log_parser = log_parser
        self.out_q = REPEAT_QUEUE
        self.logger = logging.getLogger(__name__)
        self.file_encoding = file_encoding

    def run(self):
        last_gather_ts = None
        diff_ts = None  # 回放时间与原记录时间差

        with open(self.log_file, "r", encoding=self.file_encoding) as f:

            for line in f.readlines():
                parsed = self.log_parser(line)
                parsed.parse()
                if not parsed.is_matched:  # 当该行并非请求日志时,不处理
                    continue

                if GATHER_INTERVAL == 0:  # 不控制采集间隔的情况下, 不会控制回放的节奏
                    self.logger.info("GATHER_INTERVAL eq 0")
                    self.logger.info("put an item into REPEAT_QUEUE")
                    self.logger.debug(parsed.obj_to_dict())
                    self.out_q.async_q.put_nowait(parsed.obj_to_dict())
                else:
                    if parsed.request_start_timestamp is None:
                        raise ValueError("if set GATHER_INTERVAL not eq 0, must specify the `request_start_timestamp` "
                                         "in `parse()`")
                    if last_gather_ts is None:  # 取到第一条匹配的请求日志, 回放开始
                        last_gather_ts = parsed.request_start_timestamp
                        diff_ts = int(time.time() * 1000) - last_gather_ts
                        self.logger.info("put an item into REPEAT_QUEUE")
                        self.logger.debug(parsed.obj_to_dict())
                        self.out_q.async_q.put_nowait(parsed.obj_to_dict())
                    else:
                        if parsed.request_start_timestamp - last_gather_ts <= GATHER_INTERVAL * 1000:
                            self.logger.info("put an item into REPEAT_QUEUE")
                            self.logger.debug(parsed.obj_to_dict())
                            self.out_q.async_q.put_nowait(parsed.obj_to_dict())
                        else:
                            while 1:
                                self.logger.info("will take a sleep in {} seconds".format(GATHER_INTERVAL))
                                time.sleep(GATHER_INTERVAL)
                                last_gather_ts = int(time.time()*1000) - diff_ts
                                self.logger.info("refreshed `last_gather_ts`: {}".format(last_gather_ts))
                                if parsed.request_start_timestamp - last_gather_ts < GATHER_INTERVAL * 1000:
                                    self.logger.info("put an item into REPEAT_QUEUE")
                                    self.logger.debug(parsed.obj_to_dict())
                                    self.out_q.async_q.put_nowait(parsed.obj_to_dict())
                                    break

        self.logger.info("read complete")

