import logging

import gevent.event
import gevent.greenlet
import gevent.queue
from tendrl.bridge_common.etcdobj.etcdobj import Server as etcd_server


from tendrl.node_agent.config import TendrlConfig


config = TendrlConfig()
LOG = logging.getLogger(__name__)


class deferred_call(object):

    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def call_it(self):
        self.fn(*self.args, **self.kwargs)


class Persister(gevent.greenlet.Greenlet):
    """Asynchronously persist a queue of updates.  This is for use by classes

    that maintain the primary copy of state in memory, but also lazily update

    the DB so that they can recover from it on restart.

    """

    def __init__(self):
        super(Persister, self).__init__()

        self._queue = gevent.queue.Queue()
        self._complete = gevent.event.Event()

        self._store = self.get_store()

    def update_cpu(self, cpu):
        self._store.save(cpu)

    def update_memory(self, memory):
        self._store.save(memory)

    def update_os(self, os):
        self._store.save(os)

    def update_node(self, fqdn):
        self._store.save(fqdn)

    def update_node_metadata(self, metadata):
        self._store.save(metadata)

    def _run(self):
        LOG.info("Persister listening")

        while not self._complete.is_set():
            gevent.sleep(0.1)
            pass

    def stop(self):
        self._complete.set()

    def get_store(self):
        etcd_kwargs = {'port': int(config.get("bridge_common", "etcd_port")),
                       'host': config.get("bridge_common", "etcd_connection")}
        return etcd_server(etcd_kwargs=etcd_kwargs)
