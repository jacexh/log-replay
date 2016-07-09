try:
    import simplejson as json
except (ImportError, SyntaxError):
    import json

import time
import hashlib
import logging
import logreplay
from logreplay import RequestInfo, events
import random
import string
from pythonjsonlogger import jsonlogger

record_file = 'records.log'


TERMINAL_SN = "10010000000088"
TERMINAL_KEY = "fef21baaf5fa0fc106d1be59f76a128f"

simple_fmt = "%(asctime)s - %(message)s"
thread_fmt = "%(asctime)s - %(levelname)s- %(name)s - %(funcName)s - %(threadName)s: %(message)s"


json_formatter = jsonlogger.JsonFormatter(simple_fmt, json_encoder=json.JSONEncoder)
json_file_handler = logging.FileHandler(filename='replay.log', mode='w')
json_file_handler.setFormatter(json_formatter)
json_file_handler.setLevel(logging.DEBUG)

# console_handler = logging.FileHandler('run.log', mode='w')
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter(thread_fmt)
console_handler.setFormatter(console_formatter)
console_handler.setLevel(logging.INFO)
logging.root.handlers = [console_handler]
logging.root.setLevel(logging.INFO)

REPLAY_LOGGER = logging.getLogger('replay')
REPLAY_LOGGER.setLevel(logging.DEBUG)
REPLAY_LOGGER.handlers = [json_file_handler]


def gen_rand_str(length=8, s_type='mixed', prefix=None, postfix=None):
    """
    生成指定长度的随机数，可设置输出字符串的前缀、后缀字符串
    :param length: 随机字符串长度
    :param s_type:
    :param prefix: 前缀字符串
    :param postfix: 后缀字符串
    :return:
    """
    if s_type == 'digit':
        s = string.digits
    elif s_type == 'ascii':
        s = string.ascii_letters
    elif s_type == 'hex':
        s = '0123456789abcdef'
    else:
        s = string.ascii_letters + string.digits

    ret = []
    mid = [random.choice(s) for _ in range(length)]
    if prefix is not None:
        ret.append(prefix)
    ret.extend(mid)
    if postfix is not None:
        ret.append(postfix)
    return ''.join(ret)


def md5_str(content):
    """
    计算字符串的MD5值
    :param content:输入字符串
    :return:
    """
    m = hashlib.md5(content.encode('utf-8'))
    return m.hexdigest()


class APIParse(logreplay.LogParser):

    def parse(self, line):
        info = RequestInfo(method="post", url="http://121.41.41.54:11116/upay/v2/pay")
        info.is_matched = True
        info.timestamp = int(line.strip())
        info.data = dict(dynamic_id=gen_rand_str(16, 'digit', prefix='13'), subject="mocked order", total_amount="1", terminal_sn=TERMINAL_SN)
        info.headers = {"Content-Type": "application/json"}
        return info


def repeater_handler(parameters):
    """支付网关2.0要求同一商户的client_sn不重复,通过简单的复制请求参数会导致client_sn冲突,无法进行交易"""
    client_sn = str(int(time.time() * 1000)) + gen_rand_str(4, 'digit')
    data = parameters['data']

    data['client_sn'] = client_sn
    data = json.dumps(data)

    parameters['data'] = data
    parameters['headers']['Authorization'] = TERMINAL_SN + " " + md5_str(data + TERMINAL_KEY)
    return parameters

events.repeat += repeater_handler


def callback(result):
    ret = result.result()
    ret["response"].pop("headers")
    REPLAY_LOGGER.debug("call", extra=result.result())


if __name__ == "__main__":
    logreplay.config.REPEATER_NUMBER = 5
    logreplay.config.PLAYER_NUMBER = 10
    logreplay.config.THREAD_POOL_NUMBER = 10
    logreplay.config.GATHER_INTERVAL = 2
    logreplay.config.REPEATER_HANDLER = repeater_handler
    logreplay.main(record_file, APIParse, 2, callback=callback)
