from logreplay.parser import LogParser
from logreplay.main import main
import json
from dateutil.parser import parse
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s- %(name)s - %(funcName)s - %(threadName)s: %(message)s")

record = "./api.log"


class APIParser(LogParser):

    def parse(self):
        j = json.loads(self.content)

        if not j.get('msg') == "request start":
            return
        if not (j.get('method', None) and j.get('uri', None)):
            return

        self.is_matched = True
        self.request_method = j['method']
        self.request_url = "http://121.41.41.54:8088" + j['uri']
        self.request_start_timestamp = int(parse(j['time']).timestamp() * 1000)

        if self.request_method.upper() == 'POST':
            self.request_body = json.dumps(j['form'])
        elif self.request_method.upper() == 'GET':
            self.request_body = None


if __name__ == "__main__":
    main(record, APIParser, 2)
