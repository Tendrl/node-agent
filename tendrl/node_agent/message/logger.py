import logging
from tendrl.commons.message import Message

LOG = logging.getLogger(__name__)


class Logger(object):
    logger_priorities = {"notice": "info",
                         "info": "info",
                         "error": "error",
                         "debug": "debug",
                         "warning": "warning",
                         "critical": "critical"
                         }

    def __init__(self, message):
        self.message = message
        self.push_messages()
        if self.message.job_id is not None:
            """ If job_id is present then
            it is considered as operation
            """
            self._logger(self.push_operation())
        else:
            self.push_event()
            if "exception_traceback" in message.payload:
                self._logger("%s - %s: %s" % (
                    self.message.payload["message"],
                    self.message.payload["exception_type"],
                    self.message.payload["exception_traceback"]))
            else:
                self._logger(self.message.payload["message"])

    def push_operation(self):
        NS.etcd_orm.client.write(
            "/Messages/jobs/%s" % self.message.job_id,
            Message.to_json(self.message),
            append=True)
        NS.etcd_orm.client.refresh(
            "/Messages/jobs/%s" % self.message.job_id,
            ttl=NS.config.data['message_retention_time']
        )
        log_message = ("%s:%s") % (
            self.message.job_id,
            self.message.payload["message"])
        return log_message

    def push_messages(self):
        if self.message.priority not in [
            "info", "debug"]:
            # Stroring messages cluster wise
            if self.message.cluster_id is not None:
                NS.node_agent.objects.ClusterMessage(
                    message_id=self.message.message_id,
                    timestamp=self.message.timestamp,
                    priority=self.message.priority,
                    publisher=self.message.publisher,
                    node_id=self.message.node_id,
                    payload=self.message.payload,
                    cluster_id=self.message.cluster_id,
                    job_id=self.message.job_id,
                    flow_id=self.message.flow_id,
                    parent_id=self.message.parent_id,
                    caller=self.message.caller
                ).save()
            # storing messages node wise
            else:
                NS.node_agent.objects.NodeMessage(
                    message_id=self.message.message_id,
                    timestamp=self.message.timestamp,
                    priority=self.message.priority,
                    publisher=self.message.publisher,
                    node_id=self.message.node_id,
                    payload=self.message.payload,
                    cluster_id=self.message.cluster_id,
                    job_id=self.message.job_id,
                    flow_id=self.message.flow_id,
                    parent_id=self.message.parent_id,
                    caller=self.message.caller
                ).save()

    def push_event(self):
        # storing messages in global under event
        if self.message.priority not in [
            "info", "debug"]:
            NS.node_agent.objects.Message(
                message_id=self.message.message_id,
                timestamp=self.message.timestamp,
                priority=self.message.priority,
                publisher=self.message.publisher,
                node_id=self.message.node_id,
                payload=self.message.payload,
                cluster_id=self.message.cluster_id,
                job_id=self.message.job_id,
                flow_id=self.message.flow_id,
                parent_id=self.message.parent_id,
                caller=self.message.caller
            ).save()

    def _logger(self, log_message):
        # Invalid message
        if isinstance(log_message, Message):
            log_message = Message.to_json(log_message)
        message = ("%s - %s - %s:%s - %s - %s - %s") % (
            self.message.timestamp,
            self.message.publisher,
            self.message.caller["filename"],
            self.message.caller["line_no"],
            self.message.caller["function"],
            self.message.priority.upper(),
            log_message
        )
        try:
            method = getattr(
                LOG, Logger.logger_priorities[self.message.priority])
        except AttributeError:
            raise NotImplementedError(self.message.priority)
        method(message)
