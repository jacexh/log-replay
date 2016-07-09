import json
import time
from logreplay import LogParser, RequestInfo, main, events


class ServerLogParser(LogParser):

    def parse(self, line):
        line = json.loads(line)
        ts = int(float(line['time']) * 1000)
        url = line['request']
        method = line['request_method']
        data = line['body']
        headers = line['headers']

        req_info = RequestInfo(timestamp=ts, method=method, url=url, data=data, headers=headers)
        req_info.is_matched = True
        return req_info


def update_ts(parameters):
    parameters['data'] = "ts=" + str(time.time())

events.replay += update_ts


def callback(ret):
    print(ret.result())


if __name__ == "__main__":
    main("server.log", ServerLogParser, 2, callback=callback)
