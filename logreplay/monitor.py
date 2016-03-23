import logging
import threading
import time
from .core import EVENT_LOOP, REPLAY_QUEUE, REPEAT_QUEUE, EXECUTOR, CLIENT


class MonitorThread(threading.Thread):

    def __init__(self, monitored):
        super(MonitorThread, self).__init__()
        self.monitored = monitored
        self.logger = logging

    def run(self):
        while self.monitored.isAlive():
            time.sleep(.5)
        self.logger.info("the monitored thread is dead")

        # close REPEAT_QUEUE
        while REPEAT_QUEUE.async_q.qsize():
            time.sleep(.5)
        else:
            REPEAT_QUEUE.close()
        self.logger.info("closed REPEAT_QUEUE")

        # close REPLAY_QUEUE
        while REPLAY_QUEUE.async_q.qsize():
            time.sleep(.5)
        else:
            REPLAY_QUEUE.close()
        self.logger.info("closed REPLAY_QUEUE")

        # close loop
        EXECUTOR.shutdown(wait=True)
        self.logger.info('shutdown executor')
        CLIENT.close()
        EVENT_LOOP.stop()
        try:
            EVENT_LOOP.close()
        except RuntimeError:
            pass  #

