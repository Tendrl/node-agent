# flake8: noqa
data = """---
namespace.tendrl.node_agent:
  _meta:
    platforms:
        # platform_type supported by tendrl. One of these platforms and their
        # corresponding versions must be reused in any of the definition files.
        centos:
          # platform_version
          # Supported versions, in ascending order of release. This list, being
          # ordered, enables the comparators used later in the file to function.
          - 6.x
          - 7.x
        ubuntu:
          - 15.04.x
          - 15.10.x
          - 16.04.x
    storage_system_types:
        ceph: namespace.tendrl.ceph_integration
        gluster: namespace.tendrl.gluster_integration

  objects:
    Config:
        enabled: True
        help: "Config"
        value: _tendrl/definitions/master
        list: _tendrl/definitions/master
        attrs:
            master:
                help: master definitions
                type: String

    Definition:
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

    Cpu:
      attrs:
        architecture:
          type: String
        cores_per_socket:
          type: String
        cpu_family:
          type: String
        cpu_op_mode:
          type: String
        model:
          type: String
        model_name:
          type: String
        vendor_id:
          type: String
      enabled: true
      value: nodes/$Node_context.node_id/Cpu
      help: "CPU"
    Memory:
      attrs:
        total_size:
          type: String
        total_swap:
          type: String
      enabled: true
      value: nodes/$Node_context.node_id/Memory
      help: "Node Memory"
    Service:
      attrs:
        running:
          type: String
        exists:
          type: String
        service:
          type: String
      enabled: true
      list: nodes/$Node_context.node_id/Services
      help: "Service"
      value: nodes/$Node_context.node_id/Services
    Disk:
      attrs:
        disk_id:
          help: "disk unique id"
          type: String
        device_name:
          help: "disk name"
          type: String
        disk_kernel_name:
          help: "disk internal kernel name"
          type: String
        parent_id:
          help: "disk parent id"
          type: String
        parent_name:
          help: "disk parent name"
          type: String
        disk_type:
          help: "disk type"
          type: String
        fsuuid:
          help: "file system uuid"
          type: String
        mount_point:
          help: "disk mount point"
          type: String
        Model:
          help: "disk model name"
          type: String
        vendor:
          help: "disk vendor name"
          type: String
        used:
          help: "disk used or not True/False"
          type: String
        serial_no:
          help: "disk serial number"
          type: String
        rmversion:
          help: "disk firmeware version"
          type: String
        fstype:
          help: "file system type"
          type: String
        ssd:
          help: "ssd is true / not"
          type: String
        size:
          help: "size of the disk"
          type: Integer
        device_number:
          help: "device number"
          type: String
        driver:
          help: "driver"
          type: String
        group:
          help: "disk group"
          type: String
        device:
          help: "device"
          type: String
        bios_id:
          help: "Bios id"
          type: String
        state:
          help: "disk state"
          type: String
        drive_status:
          help: "disk status"
          type: String
        label:
          help: "label"
          type: String
        req_queue_size:
          help: "request queue size"
          type: String
        driver_modules:
          help: "driver modules"
          type: String
        mode:
          help: "driver mode"
          type: String
        owner:
          help: "driver owner"
          type: String
        min_io_size:
          help: "min I/O size"
          type: String
        major_to_minor_no:
          help: "major to minor number"
          type: String
        device_files:
          help: "device files"
          type: String
        sysfs_busid:
          help: "sysfs bus id"
          type: String
        alignement:
          help: "alignement"
          type: String
        read_only:
          help: "disk is read only or not"
          type: String
        read_ahead:
          help: "read ahead"
          type: String
        removable_device:
          help: "removable device or not"
          type: String
        scheduler_name:
          help: "scheduler_name"
          type: String
        sysfs_id:
          help: "sysfs id"
          type: String
        sysfs_device_link:
          help: "sysfs device link"
          type: String
        geo_bios_edd:
          help: "geometry bios edd"
          type: String
        geo_bios_legacy:
          help: "geometry bios legacy"
          type: String
        geo_logical:
          help: "geometry logical"
          type: String
        phy_sector_size:
          help: "physical sector size"
          type: String
        discard_granularity:
          help: "discard granularity"
          type: String
        discard_align_offset:
          help: "discard align offset"
          type: String
        discard_max_bytes:
          help: "discard max bytes"
          type: String
        discard_zeroes_data:
          help: "discard zeroes data"
          type: String
        optimal_io_size:
          help: "optimal I/O size"
          type: String
        log_sector_size:
          help: "logical sector size"
          type: String

      enabled: true
      list: nodes/$Node_context.node_id/Disks
      value: nodes/$Node_context.node_id/Disks
      help: "Disk"
    UsedDisk:
      attrs:
        disk_id:
          help: "File system UUID"
          type: String
      enabled: true
      list: nodes/$Node_context.node_id/Disks/used
    FreeDisk:
      attrs:
        disk_id:
          help: "File system UUID"
          type: String
      enabled: true
      list: nodes/$Node_context.node_id/Disks/free
    Node:
      atoms:
        cmd:
          enabled: true
          inputs:
            mandatory:
              - Node.cmd_str
          name: "Execute CMD on Node"
          help: "Executes a command"
          run: tendrl.node_agent.atoms.node.cmd.Cmd
          type: Create
          uuid: dc8fff3a-34d9-4786-9282-55eff6abb6c3
        check_node_up:
          enabled: true
          inputs:
            mandatory:
              - Node.fqdn
          outputs:
            - Node.status
          name: "check whether the node is up"
          help: "Checks if a node is up"
          run: tendrl.node_agent.atoms.node.check_node_up
          type: Create
          uuid: eda0b13a-7362-48d5-b5ca-4b6d6533a5ab
      attrs:
        fqdn:
          type: String
        status:
          type: Boolean
      enabled: true
      value: nodes/$Node_context.node_id/Node
      help: "Node"
    Os:
      attrs:
        kernel_version:
          type: String
        os:
          type: String
        os_version:
          type: String
        selinux_mode:
          type: String
      enabled: true
      value: nodes/$Node_context.node_id/Os
      help: "OS"
    Package:
      atoms:
        install:
          enabled: true
          inputs:
            mandatory:
              - Package.name
              - Package.pkg_type
            optional:
              - Package.version
          name: "Install Package"
          help: "Checks if a package is installed"
          post_run:
            - tendrl.node_agent.atoms.package.validations.check_package_installed
          run: tendrl.node_agent.atoms.package.install.Install
          type: Create
          uuid: 16abcfd0-aca9-4022-aa0f-5de1c5a742c7
      attrs:
        name:
          help: "Location of the rpm/deb/pypi package"
          type: String
        pkg_type:
          help: "Type of package can be rpm/deb/pip/"
        state:
          help: "State can installed|uninstalled"
        version:
          help: "Version of the rpm/deb/pypi package"
          type: String
      enabled: true
      help: "package"
      value: ""
    Process:
      atoms:
        start:
          enabled: true
          inputs:
            mandatory:
              - Service.config_path
              - Service.config_data
          name: "Configure Service"
          help: "Checks if a service is running"
          post_run:
            - tendrl.node_agent.atoms.service.validations.check_service_running
          run: tendrl.node_agent.atoms.service.configure.Configure
          type: Update
          uuid: b90a0d97-8c9f-4ab1-8f64-dbb5638159a3
      attrs:
        name:
          help: "Name of the service"
          type: String
        state:
          help: "Service state can be started|stopped|restarted|reloaded"
          type: String
      enabled: true
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
    NodeContext:
      attrs:
        machine_id:
          help: "Unique /etc/machine-id"
          type: String
        fqdn:
          help: "FQDN of the Tendrl managed node"
          type: String
        node_id:
          help: "Tendrl ID for the managed node"
          type: String
        tags:
          help: "The tags associated with this node"
          type: String
        status:
          help: "Node status"
          type: String

      enabled: true
      list: nodes/$Node_context.node_id/Node_context
      value: nodes/$Node_context.node_id/Node_context
      help: Node Context
    File:
      atoms:
        write:
          enabled: true
          inputs:
            mandatory:
              - Config.data
              - Config.file_path
          name: "Write configuration data"
          help: "Writes the configuration data"
          run: tendrl.node_agent.objects.File.atoms.write.Write
          uuid: b90a0d97-8c9f-4ab1-8f64-dbb5638159a5
      attrs:
        data:
          help: "Configuration data"
          type: String
        file_path:
          help: "configuration file path"
          type: String
      enabled: true
      help: "File"
      value: ""
    Platform:
      attrs:
        kernel_version:
          type: String
        os:
          type: String
        os_version:
          type: String
      enabled: true
      help: "Platform of the Node"
      value: nodes/$Node_context.node_id/Platform
      list: nodes/$Node_context.node_id/Platform
namespace.tendrl.node_agent.gluster_integration:
  flows:
    ImportCluster:
      atoms:
        - tendrl.node_agent.objects.Package.atoms.install
        - tendrl.node_agent.gluster_integration.objects.Config.atoms.generate
        - tendrl.node_agent.objects.File.atoms.write
        - tendrl.node_agent.objects.Node.atoms.cmd
      help: "Import existing Gluster Cluster"
      enabled: true
      inputs:
        mandatory:
          - "Node[]"
          - Tendrl_context.sds_name
          - Tendrl_context.sds_version
          - Tendrl_context.cluster_id
      post_run:
        - tendrl.node_agent.gluster_integration.objects.Tendrl_context.atoms.check_cluster_id_exists
      pre_run:
        - tendrl.node_agent.objects.Node.atoms.check_node_up
        - tendrl.node_agent.objects.Tendrl_context.atoms.compare
      run: tendrl.node_agent.gluster_integration.flows.import_cluster.ImportCluster
      type: Create
      uuid: 2f94a48a-05d7-408c-b400-e27827f4edef
      version: 1
  objects:
    Tendrl_context:
      atoms:
        check_cluster_id_exists:
          enabled: true
          name: "Check cluster id existence"
          help: "Checks if a cluster id exists"
          run: tendrl.node_agent.gluster_integration.objects.Tendrl_context.atoms.check_cluster_id_exists.CheckClusterIdExists
          uuid: b90a0d97-8c9f-4ab1-8f64-dbb5638159a4
      enabled: True
      attrs:
        cluster_id:
          help: "Tendrl managed/generated cluster id for the sds being managed by Tendrl"
          type: String
        sds_name:
          help: "Name of the Tendrl managed sds, eg: 'gluster'"
          type: String
        sds_version:
          help: "Version of the Tendrl managed sds, eg: '3.2.1'"
          type: String
      value: clusters/$Tendrl_context.cluster_id/Tendrl_context
    Config:
      atoms:
        generate:
          enabled: true
          inputs:
            mandatory:
              - Config.etcd_port
              - Config.etcd_connection
          name: "Generate Gluster Integration configuration based on provided inputs"
          help: "Generates configuration content"
          outputs:
            - Config.data
            - Config.file_path
          run: tendrl.node_agent.gluster_integration.objects.Config.atoms.generate.Generate
          uuid: 807a1ead-bd70-4f55-99d0-dbd9d76d2a10
      attrs:
        data:
          help: "Configuration data of Gluster Integration for this Tendrl deployment"
          type: String
        etcd_connection:
          help: "Host/IP of the etcd central store for this Tendrl deployment"
          type: String
        etcd_port:
          help: "Port of the etcd central store for this Tendrl deployment"
          type: String
        file_path:
          default: /etc/tendrl/gluster_integration.conf
          help: "Path to the Gluster integration tendrl configuration"
          type: String
      enabled: true

namespace.tendrl.node_agent.ceph_integration:
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
          - Tendrl_context.sds_name
          - Tendrl_context.sds_version
          - Tendrl_context.cluster_id
      post_run:
        - tendrl.node_agent.ceph_integration.objects.Tendrl_context.atoms.check_cluster_id_exists
      pre_run:
        - tendrl.node_agent.objects.Node.atoms.check_node_up
        - tendrl.node_agent.objects.Tendrl_context.atoms.compare
      run: tendrl.node_agent.ceph_integration.flows.import_cluster.ImportCluster
      type: Create
      uuid: 5a48d43b-a163-496c-b01d-9c600ea0a5db
      version: 1
  objects:
    Tendrl_context:
      atoms:
        check_cluster_id_exists:
          enabled: true
          name: "Check cluster id existence"
          help: "Checks if a cluster id exists"
          run: tendrl.node_agent.ceph_integration.objects.Tendrl_context.atoms.check_cluster_id_exists.CheckClusterIdExists
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
      value: clusters/$Tendrl_context.cluster_id/Tendrl_context
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

tendrl_schema_version: 0.3
"""
