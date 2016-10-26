import gevent.event


class SampleManager(object):
    """sample manager for mocking

    """

    def __init__(self):
        self._complete = gevent.event.Event()

    def stop(self):
        pass

    def _recover(self):
        pass

    def start(self):
        pass

    def join(self):
        pass
