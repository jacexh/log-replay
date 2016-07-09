import logging
import asyncio
import threading
import time
from . import config
from .core import REPEAT_QUEUE, CLIENT


class MonitorThread(threading.Thread):

    def __init__(self, monitored):
        super(MonitorThread, self).__init__()
        self.monitored = monitored
        self.logger = logging

    def run(self):
        while self.monitored.isAlive():
            time.sleep(.5)
        self.logger.info("the monitored thread is dead")

        event_loop = asyncio.get_event_loop()
        # send finish signal to REPEAT_QUEUE
        self.logger.info('send finish signal to REPEAT_QUEUE')
        event_loop.call_soon_threadsafe(REPEAT_QUEUE.put_nowait, config.FINISHED_SIGNAL)

        # close loop
        self.logger.info('shutdown client and stop event loop')

        event_loop.call_soon_threadsafe(CLIENT.close)
        event_loop.call_soon_threadsafe(event_loop.stop)
