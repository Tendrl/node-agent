# flake8: noqa
data = """---
namespace.tendrl.node_agent:
  objects:
    Definition:
        enabled: True
        help: "Definition"
        value: _tendrl/definitions/data
        list: _tendrl/definitions/data
        attrs:
            master:
                help: master definitions
                type: String
    Config:
        enabled: True
        help: "Config"
        value: _tendrl/config/data
        list: _tendrl/config/
        attrs:
            data:
                help: config
                type: String
    TendrlContext:
      enabled: True
      attrs:
        integration_id:
          help: "Tendrl managed/generated cluster id for the sds being managed by Tendrl"
          type: String
        sds_name:
          help: "Name of the Tendrl managed sds, eg: 'gluster'"
          type: String
        sds_version:
          help: "Version of the Tendrl managed sds, eg: '3.2.1'"
          type: String
        node_id:
          help: "Tendrl ID for the managed node"
          type: String
      value: nodes/$Node_context.node_id/TendrlContext
      help: "Tendrl context"
tendrl_schema_version: 0.3
"""
