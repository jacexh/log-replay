import logging
import asyncio
import threading
import time
from . import config
from .core import REPEAT_QUEUE, CLIENT, EVENT_LOOP


class MonitorThread(threading.Thread):

    def __init__(self, monitored):
        super(MonitorThread, self).__init__()
        self.monitored = monitored
        self.logger = logging

    def run(self):
        while self.monitored.isAlive():
            time.sleep(.5)
        self.logger.info("the monitored thread is dead")

        # send finished signal to all repeater
        self.logger.info('send finish signal to REPEAT_QUEUE')
        for _ in range(config.REPEATER_NUMBER):
            EVENT_LOOP.call_soon_threadsafe(REPEAT_QUEUE.put_nowait, config.FINISHED_SIGNAL)

        self.logger.info("waiting for all tasks to complete")
        while asyncio.Task.all_tasks(loop=EVENT_LOOP):
            time.sleep(.5)

        # close loop
        self.logger.info('stop event loop safety')
        EVENT_LOOP.call_soon_threadsafe(CLIENT.close)
        EVENT_LOOP.call_soon_threadsafe(EVENT_LOOP.stop)
