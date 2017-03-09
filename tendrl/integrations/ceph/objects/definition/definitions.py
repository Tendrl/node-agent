data = """namespace.tendrl.integrations.ceph:
  flows:
    ImportCluster:
      atoms:
        - tendrl.node_agent.objects.Package.atoms.install
        - tendrl.node_agent.ceph_integration.objects.Config.atoms.generate
        - tendrl.node_agent.objects.File.atoms.write
        - tendrl.node_agent.objects.Node.atoms.cmd
      help: "Import existing Ceph Cluster"
      enabled: true
      inputs:
        mandatory:
          - "Node[]"
          - TendrlContext.sds_name
          - TendrlContext.sds_version
          - TendrlContext.integration_id
      post_run:
        - tendrl.node_agent.ceph_integration.objects.TendrlContext.atoms.check_cluster_id_exists
      pre_run:
        - tendrl.node_agent.objects.Node.atoms.check_node_up
        - tendrl.node_agent.objects.TendrlContext.atoms.compare
      run: tendrl.node_agent.ceph_integration.flows.import_cluster.ImportCluster
      type: Create
      uuid: 5a48d43b-a163-496c-b01d-9c600ea0a5db
      version: 1
  objects:
    TendrlContext:
      atoms:
        check_cluster_id_exists:
          enabled: true
          name: "Check cluster id existence"
          help: "Checks if a cluster id exists"
          run: tendrl.node_agent.ceph_integration.objects.TendrlContext.atoms.check_cluster_id_exists.CheckClusterIdExists
          uuid: b90a0d97-8c9f-4ab1-8f64-dbb5638159a1
      enabled: True
      attrs:
        cluster_id:
          help: "Tendrl managed/generated cluster id for the sds being managed by Tendrl"
          type: String
        sds_name:
          help: "Name of the Tendrl managed sds, eg: 'ceph'"
          type: String
        sds_version:
          help: "Version of the Tendrl managed sds, eg: '2.1'"
          type: String
      value: clusters/$TendrlContext.integration_id/TendrlContext
    Config:
      atoms:
        generate:
          enabled: true
          inputs:
            mandatory:
              - Config.etcd_port
              - Config.etcd_connection
          name: "Generate Ceph Integration configuration based on provided inputs"
          help: "Generates configuration content"
          outputs:
            - Config.data
            - Config.file_path
          run: tendrl.node_agent.ceph_integration.objects.Config.atoms.generate.Generate
          uuid: 61959242-628f-4847-a5e2-2c8d8daac0cd
      attrs:
        data:
          help: "Configuration data of Ceph Integration for this Tendrl deployment"
          type: String
        etcd_connection:
          help: "Host/IP of the etcd central store for this Tendrl deployment"
          type: String
        etcd_port:
          help: "Port of the etcd central store for this Tendrl deployment"
          type: String
        file_path:
          default: /etc/tendrl/ceph_integration.conf
          help: "Path to the Ceph integration tendrl configuration"
          type: String
      enabled: true
"""