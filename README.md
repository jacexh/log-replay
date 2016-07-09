基于日志回放http请求工具
==============

**仅支持Python 3.5**

## Example:

### 日志内容如下:

单行显示

```json
{
  "time": "1468060658.21",
  "status": "200",
  "request": "http://requestb.in/1m7dv4o1",
  "request_method": "POST",
  "body": "ts=1468060658.21",
  "headers": {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "python-requests/2.10.0",
    "Connection": "close"
  }
}
```

### 代码如下:

```python
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
```

### 执行结果:

```
{'request': {'headers': {'Connection': 'close', 'User-Agent': 'python-requests/2.10.0', 'Content-Type': 'application/x-www-form-urlencoded'}, 'data': 'ts=1468061309.565184', 'params': None}, 'response': {'headers': <CIMultiDictProxy('DATE': 'Sat, 09 Jul 2016 10:48:30 GMT', 'CONTENT-TYPE': 'text/html; charset=utf-8', 'TRANSFER-ENCODING': 'chunked', 'CONNECTION': 'close', 'SET-COOKIE': '__cfduid=d755539979cb41531996566a44a5858301468061310; expires=Sun, 09-Jul-17 10:48:30 GMT; path=/; domain=.requestb.in; HttpOnly', 'SPONSORED-BY': 'https://www.runscope.com', 'VIA': '1.1 vegur', 'SERVER': 'cloudflare-nginx', 'CF-RAY': '2bfb34356730511c-SJC', 'CONTENT-ENCODING': 'gzip')>, 'content': 'ok', 'method': 'POST', 'status_code': 200, 'cookies': <SimpleCookie: __cfduid='d755539979cb41531996566a44a5858301468061310'>, 'latency': 1027, 'url': 'http://requestb.in/1m7dv4o1'}}
{'request': {'headers': {'Connection': 'close', 'User-Agent': 'python-requests/2.10.0', 'Content-Type': 'application/x-www-form-urlencoded'}, 'data': 'ts=1468061309.561715', 'params': None}, 'response': {'headers': <CIMultiDictProxy('DATE': 'Sat, 09 Jul 2016 10:48:30 GMT', 'CONTENT-TYPE': 'text/html; charset=utf-8', 'TRANSFER-ENCODING': 'chunked', 'CONNECTION': 'close', 'SET-COOKIE': '__cfduid=d53eab9061cc31b78a955e1611820e4dd1468061310; expires=Sun, 09-Jul-17 10:48:30 GMT; path=/; domain=.requestb.in; HttpOnly', 'SPONSORED-BY': 'https://www.runscope.com', 'VIA': '1.1 vegur', 'SERVER': 'cloudflare-nginx', 'CF-RAY': '2bfb3435acdf2246-LAX', 'CONTENT-ENCODING': 'gzip')>, 'content': 'ok', 'method': 'POST', 'status_code': 200, 'cookies': <SimpleCookie: __cfduid='d53eab9061cc31b78a955e1611820e4dd1468061310'>, 'latency': 1389, 'url': 'http://requestb.in/1m7dv4o1'}}
```