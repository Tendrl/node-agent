from tendrl.commons.etcdobj import EtcdObj
from tendrl.commons import objects


class JournalMapping(objects.BaseObject):
    def __init__(self, node_id=None, storage_disks=None,
                 unallocated_disks=None, *args, **kwargs):
        super(JournalMapping, self).__init__(*args, **kwargs)

        self.value = '_tmp/%s/journal_mapping/%s'
        self.node_id = node_id
        self.storage_disks = storage_disks
        self.unallocated_disks = unallocated_disks
        self._etcd_cls = _JournalMapping


class _JournalMapping(EtcdObj):
    __name__ = '_tmp/%s/journal_mapping/%s'
    _tendrl_cls = JournalMapping

    def render(self):
        self.__name__ = self.__name__ % \
            (NS.tendrl_context.integration_id, self.node_id)
        return super(_JournalMapping, self).render()
