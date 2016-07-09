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

        self.logger.info("waiting for all tasks to complete")
        while asyncio.Task.all_tasks(loop=event_loop):
            time.sleep(.5)

        # close loop
        self.logger.info('stop event loop safety')
        event_loop.call_soon_threadsafe(CLIENT.close)
        event_loop.call_soon_threadsafe(event_loop.stop)
