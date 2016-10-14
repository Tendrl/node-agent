import logging
import signal

import gevent.event
import gevent.greenlet

from rpc import EtcdThread
from tendrl.node_agent import log

LOG = logging.getLogger(__name__)


class Manager(object):
    """manage user request thread

    """

    def __init__(self):
        self._complete = gevent.event.Event()

        self._user_request_thread = EtcdThread(self)

    def stop(self):
        LOG.info("%s stopping" % self.__class__.__name__)
        self._user_request_thread.stop()

    def _recover(self):
        LOG.debug("Recovered server")
        pass

    def start(self):
        LOG.info("%s starting" % self.__class__.__name__)
        self._user_request_thread.start()

    def join(self):
        LOG.info("%s joining" % self.__class__.__name__)
        self._user_request_thread.join()


def main():
    log.setup_logging()
    m = Manager()
    m.start()

    complete = gevent.event.Event()

    def shutdown():
        LOG.info("Signal handler: stopping")
        complete.set()

    gevent.signal(signal.SIGTERM, shutdown)
    gevent.signal(signal.SIGINT, shutdown)

    while not complete.is_set():
        complete.wait(timeout=1)


if __name__ == "__main__":
    main()
