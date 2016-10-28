import logging

import gevent.event
import gevent.greenlet
import gevent.queue
from tendrl.bridge_common.etcdobj.etcdobj import Server as etcd_server


from tendrl.node_agent.config import TendrlConfig
from tendrl.node_agent.persistence.sync_objects import SyncObject


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

    def __getattribute__(self, item):
        """Wrap functions with LOGging

        """
        if item.startswith('_'):
            return object.__getattribute__(self, item)
        else:
            try:
                return object.__getattribute__(self, item)
            except AttributeError:
                try:
                    attr = object.__getattribute__(self, "_%s" % item)
                    if callable(attr):
                        def defer(*args, **kwargs):
                            dc = deferred_call(attr, args, kwargs)
                            try:
                                dc.call_it()
                            except Exception as ex:
                                LOG.exception(
                                    "Persister exception persisting "
                                    "data: %s" % (dc.fn,)
                                )
                                LOG.exception(ex)
                        return defer
                    else:
                        return object.__getattribute__(self, item)
                except AttributeError:
                    return object.__getattribute__(self, item)

    def update_sync_object(self, updated, data):
        try:
            self._store.save(SyncObject(updated=updated, data=data))
        except Exception as e:
            LOG.info("ERROR while saving: %s" % str(e))

    def update_cpu(self, cpu):
        self._store.save(cpu)

    def update_memory(self, memory):
        self._store.save(memory)

    def update_node(self, node):
        try:
            self._store.save(node)
        except Exception as e:
            LOG.info("ERROR while saving: %s" % str(e))

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
