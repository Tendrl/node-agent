import json
import logging
import re
import traceback
import uuid

import etcd
import gevent.event
import yaml

from tendrl.node_agent.config import TendrlConfig
from tendrl.node_agent.flows.flow_execution_exception import \
    FlowExecutionFailedError
from tendrl.node_agent.manager.command import Command
from tendrl.node_agent.manager import utils
from tendrl.bridge_common.definitions.validator import \
    DefinitionsSchemaValidator, JobValidator

config = TendrlConfig()
LOG = logging.getLogger(__name__)


class EtcdRPC(object):

    def __init__(self):
        etcd_kwargs = {'port': int(config.get("bridge_common", "etcd_port")),
                       'host': config.get("bridge_common", "etcd_connection")}

        self.client = etcd.Client(**etcd_kwargs)
        node_agent_key = utils.configure_tendrl_uuid()
        cmd = Command({"_raw_params": "cat %s" % node_agent_key})
        out, err = cmd.start()
        self.node_id = out['stdout']

    def _process_job(self, raw_job, job_key):
        # Pick up the "new" job that is not locked by any other bridge
        if raw_job['status'] == "new" and raw_job["type"] == "node":
                raw_job['status'] = "processing"
                # Generate a request ID for tracking this job
                # further by tendrl-api
                req_id = str(uuid.uuid4())
                raw_job['request_id'] = "%s/flow_%s" % (
                    self.node_id, req_id)
                self.client.write(job_key, json.dumps(raw_job))
                LOG.info("Processing JOB %s" % raw_job[
                    'request_id'])
                try:
                    definitions = self.validate_flow(raw_job)
                    if definitions:
                        result, err = self.invoke_flow(
                        raw_job['run'], raw_job, definitions
                        )
                except FlowExecutionFailedError as e:
                    LOG.error(e)
                    raise
                if err != "":
                    raw_job['status'] = "failed"
                    LOG.error("JOB %s Failed. Error: %s" % (raw_job[
                        'request_id'], err))
                else:
                    raw_job['status'] = "finished"

                raw_job["response"] = {
                    "result": result,
                    "error": err
                }
                return raw_job, True
        else:
            return raw_job, False

    def _acceptor(self):
        while True:
            jobs = self.client.read("/queue")
            gevent.sleep(2)
            for job in jobs.children:
                executed = False
                raw_job = json.loads(job.value.decode('utf-8'))
                try:
                    raw_job, executed = self._process_job(raw_job, job.key)
                except FlowExecutionFailedError as e:
                    LOG.error("Failed to execute job: %s. Error: %s" % (
                        str(job), str(e)))

                if executed:
                    self.client.write(job.key, json.dumps(raw_job))
                    break

    def run(self):
        self._acceptor()

    def stop(self):
        pass

    def validate_flow(self, raw_job):
        LOG.info("Validating flow %s for %s" % (raw_job['run'],
                                                raw_job['request_id']))
        definitions = yaml.load(self.client.read(
            '/tendrl_definitions_node_agent/data'))
        definitions = DefinitionsSchemaValidator(
            definitions).sanitize_definitions()
        resp, msg = JobValidator(definitions).validateApi(raw_job)
        if resp:
            msg = "Successfull Validation flow %s for %s" %\
                  (raw_job['run'], raw_job['request_id'])
            LOG.info(msg)

            return definitions
        else:
            msg = "Failed Validation flow %s for %s" % (raw_job['run'],
                                                        raw_job['request_id'])
            LOG.error(msg)
            return False


    def invoke_flow(self, flow_name, job, definitions):
        atoms, pre_run, post_run, uuid= self.extract_flow_details(flow_name,
                                                                  definitions)
        the_flow = None
        flow_path = flow_name.lower().split(".")
        flow_module = flow_path[:-1]
        kls_name = flow_path[-1:]
        if "tendrl" in flow_path and "flows" in flow_path:
            exec("from %s import %s as the_flow" % (flow_module, kls_name))
            return the_flow(flow_name, job, atoms, pre_run, post_run,
                            uuid).run()

    def extract_flow_details(self, flow_name, definitions):
        namespace = flow_name.split(".flows.")
        flow = definitions[namespace][flow_name.split(".")[-1]]
        return flow['atoms'], flow['pre_run'], flow['post_run'], flow['uuid']

class EtcdThread(gevent.greenlet.Greenlet):
    """Present a ZeroRPC API for users

    to request state changes.

    """

    # In case server.run throws an exception, prevent
    # really aggressive spinning
    EXCEPTION_BACKOFF = 5

    def __init__(self, manager):
        super(EtcdThread, self).__init__()
        self._manager = manager
        self._complete = gevent.event.Event()
        self._server = EtcdRPC()

    def stop(self):
        LOG.info("%s stopping" % self.__class__.__name__)

        self._complete.set()
        if self._server:
            self._server.stop()

    def _run(self):

        while not self._complete.is_set():
            try:
                LOG.info("%s run..." % self.__class__.__name__)
                self._server.run()
            except Exception:
                LOG.error(traceback.format_exc())
                self._complete.wait(self.EXCEPTION_BACKOFF)

        LOG.info("%s complete..." % self.__class__.__name__)
