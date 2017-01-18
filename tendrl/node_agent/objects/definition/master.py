# flake8: noqa
data = """---
namespace.tendrl.node_agent:
  objects:
    Cpu:
      attrs:
        architecture:
          type: String
        cores_per_socket:
          type: String
        cpu_count:
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
    Memory:
      attrs:
        total_size:
          type: String
        total_swap:
          type: String
      enabled: true
      value: nodes/$Node_context.node_id/Memory
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
        cmd_str:
          type: String
        fqdn:
          type: String
        status:
          type: Boolean
      enabled: true
      value: nodes/$Node_context.node_id/Node
    OS:
      attrs:
        kernel_version:
          type: String
        os:
          type: String
        os_varsion:
          type: String
        selinux_mode:
          type: String
      enabled: true
      value: nodes/$Node_context.node_id/Os
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
    Service:
      atoms:
        configure:
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
        config_data:
          help: "Configuration data for the service"
          type: String
        config_path:
          help: "configuration file path for the service eg:/etc/tendrl/tendrl.conf"
          type: String
        name:
          help: "Name of the service"
          type: String
        state:
          help: "Service state can be started|stopped|restarted|reloaded"
          type: String
      enabled: true
    Tendrl_context:
      atoms:
        compare:
          enabled: true
          inputs:
            mandatory:
              - Tendrl_context.sds_name
              - Tendrl_context.sds_version
          name: "Compare SDS details"
          help: "Compares the SDS details in context"
          run: tendrl.node_agent.objects.tendrl_context.atoms.compare.Compare
          uuid: b90a0d97-8c9f-4ab1-8f64-dbb5638159a9
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
        node_id:
          help: "Tendrl ID for the managed node"
          type: String
      value: nodes/$Node_context.node_id/Tendrl_context
    Node_context:
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
        cluster_id:
          help: Id of the cluster to which node belongs to
          type: String
        sds_pkg_name:
          help: Storage system package name
          type: String
        sds_pkg_version:
          help: Storage system package version
          type: String
        detected_cluster_id:
          help: Detected cluster id
          type: String
        cluster_attrs:
          help: Additional cluster specific attributes
          type: json
      enabled: true
      value: nodes/$Node_context.node_id/Node_context
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
    Platform:
      attrs:
        kernel_version:
          type: String
        os:
          type: String
        os_version:
          type: String
      enabled: true
      value: nodes/$Node_context.node_id/Platform
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


data_exp = """# The global tendrl namespace would consist mostly of hardcoded keys and
# values. Most of these keys and values would be reused in all the other
# definition files. The code associated with this namespace would also
# contain specific logic to handle the declarations in this section and the
# corresponding references from the other namespaces of the definition files.
namespace.tendrl:
  # Installation sources define the supported installation methods and the
  # parameters that need to be supplied for using that method. This being in
  # the global tendrl namespace, defines the expected data types. These
  # values would be used by the validations to ensure that wherever the
  # `installation_sources` section is used, outside this global namespace, it
  # conforms to the definitions provided.
  #
  # Each installation_type contains a list of mandatory parameters. Along
  # with these, variables could be populated on the fly. These need to be
  # supplied as `parameters` from the appropriate `installation` sections.
  installation_sources:
    # installation_type
    yum_repository:
      # Configure the yum repository. Doesn't actually install anything.
      repository_path: String
      gpgcheck: Boolean
      packages: Hash
    yum:
      # Install packages using yum. Assume that the repositories have already
      # been configured.
      # The value supplied needs to be {name:version,name:version}
      packages: Hash
    git:
      repository_path: String
      # tag, branch or commit id
      reference: String
    pip_package:
      package_name: String
      # "latest" is a supported version, which will automatically use the
      # latest available.
      package_version: String
    pip_requirements:
      requirements_file: String
    git+pip_requirements: Hash
      # It is possible to chain multiple installation methods together. In
      # which case, they'll be invoked in the order specified and the
      # parameters would be required based on their individual definitions.
    yum_repository+yum: Hash
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
  invocations:
    service:
      # systemd service
      # implementation module: tendrl.global.Invocations.Service
      parameters:
        name: String
        start_action: String
        stop_action: String
    cli:
      # Generic CLI command
      # implementation module: tendrl.global.Invocations.Cli
      parameters:
        # Array of objects
        - command: String
          # Provide either a list of success or failure exit codes. Anything
          # else would indicate the other condition.
          success_exit_code: Array
    module:
      # A specific module in the code
      parameters:
        - module: Module
          parameters: Hash
  storage_system_types:
    ceph: namespace.tendrl.integrations.ceph
    gluster: namespace.tendrl.integrations.gluster
namespace.tendrl.integrations.ceph:
  node_roles:
    - mon
    - osd
  detection_roles:
    # detection module: role to be assigned if detected
    ceph_mon: mon
    ceph_osd: osd
  provisioners:
    # provisioner_type: provisioner specific namespace
    ceph-installer: namespace.tendrl.integrations.ceph.provisioner.ceph_installer
    ceph-ansible: namespace.tendrl.integrations.ceph.provisioner.ceph_ansible
  integration:
    installation_sources:
      # Sections that define a list of things don't need the `type`
      # attribute. Essentially, a definition section simply lists
      # alternatives and their details. A section somewhere later then
      # references one of the defined objects. In such a scenario, it's a
      # specific instantiation of the definition and requires a `type`
      # attribute.
      git+pip_requirements:
        parameters:
          ceph_integration_version: namespace.tendrl.installation_sources.git.TagVersion
        repository_path: https://github.com/Tendrl/ceph_integration.git
        reference: $ceph_integration_version
        requirements_file: requirements.txt
        invocation:
          # Here, the invocation section instantiates a specific type of
          # object from the available ones defined in the global
          # invocations list. Hence, the `type` attribute is required. Only
          # one specific object can be instantiated via `type`, so the
          # parameters are automatically applied to that specific object.
          # The invocation section contains an ordered list of invocations to
          # be executed one time, post installation.
          - type: cli
            parameters:
              - command: 'bin/ceph_integration'
                success_exit_code: [0]
      yum_repository+yum:
        parameters:
          repo_system_version: namespace.tendrl.platforms.centos.RepoVersionString
        repository_path: http://tendrl.org/repos/ceph-integration/yum/$repo_system_version/
        packages: [tendrl-integration-ceph]
        invocation:
          - type: service
            parameters:
              name: tendrl-ceph-integration.service
              start-action: start
              stop-action: stop
  versions:
    # Versions can be with or without the .x wildcard. Without the
    # wildcard, specific version will be matched.
    2.0:
      # Keys must reference the keys from the platforms section.
      ubuntu:
        # Versions can use comparators, along with the values from the
        # list of supported versions from the platform type.
        >=15.04:
          provisioner:
            # The type is used to resolve to the appropriate namespace
            # based on the `provisioners` section.
            type: ceph-ansible
            installation:
              # The installation section here would provide the variables
              # required by the installation_sources section in the
              # provisioner's namespace.
              type: git
              parameters:
                provisioner_version: 2.0
          integration:
            installation:
              type: git+pip_requirements
              parameters:
                ceph_integration_version: 1.0.x
      centos:
        =6.x:
          provisioner:
            type: ceph-installer
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el6
          integration:
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el6
    2.1.x:
      ubuntu:
        # The + operator has been used to combine multiple versions to
        # create a range.
        >=15.10+<=16.04:
          provisioner:
            type: ceph-ansible
            installation:
              type: git
              parameters:
                provisioner_version: 2.1.x
          integration:
            installation:
              type: git+pip_requirements
              parameters:
                ceph_integration_version: 1.2.x
      centos:
        # The .x wildcard here has been used to ensure that any versions
        # in the 7 series only, above 7.4, will be supported.
        >=7.4.x:
          provisioner:
            type: ceph-installer
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el7
          integration:
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el7
namespace.tendrl.integrations.ceph.provisioner.ceph_installer:
  installation_sources:
    yum_repository+yum:
      parameters:
        repo_system_version: namespace.tendrl.platforms.centos.RepoVersionString
      repository_path: http://ceph-installer.org/repos/yum/$repo_system_version/x86_64/
      packages: [ceph_installer]
      invocation:
        # Invocations are referenced from the global `invocations`
        # declarations. Invocation sections are necessary in cases where a
        # a one-time post installation activity is needed, such as a
        # service to be started. The actual integration and interaction
        # with the system is coded in the wrapper based on the flows.
        - type: module
          parameters:
            - module: Tendrl.Provisioning.SetupSsh
              parameters: `tendrl_context.nodes`
        - type: service
          parameters:
            name: ceph-installer.service
            start_action: start
            stop_action: stop
    git:
      parameters:
        provisioner_version: namespace.tendrl.installation_sources.git.TagVersion
      repository_path: https://github.com/ceph/ceph-installer.git
      reference: $provisioner_version
      invocation:
        - type: cli
          parameters:
            - command: 'bin/ceph-installer setup'
              success_exit_code: [0]
            - command: 'bin/ceph-installer start'
              success_exit_code: [0]
        - type: module
          parameters:
            - module: Tendrl.Provisioning.SetupSsh
              parameters: `tendrl_context.nodes`
namespace.tendrl.integrations.ceph.provisioner.ceph_ansible:
  installation_sources:
    git:
      repository_path: https://github.com/ceph/ceph-ansible.git
      reference: $provisioner_version
      # The lack of an invocation section means there's no invocation to be
      # done post installation. The actual integration wrapper code
      # implements all the necessary actions to integrate with the
      invocation:
        - type: module
          parameters:
            - module: Tendrl.Provisioning.SetupSsh
              parameters: `tendrl_context.nodes`
        - type: cli
          parameters:
            - command: 'bin/setup'
              success_exit_code: [0]
namespace.tendrl.integrations.gluster:
  node_roles:
    - glusterd
  detection_roles:
    # detection module: role to be assigned if detected
    glusterd: glusterd
  provisioners:
    gdeploy: namespace.tendrl.integrations.gluster.provisioner.gdeploy
  integration:
    installation_sources:
      yum:
        parameters:
          repo_system_version: namespace.tendrl.platforms.centos.RepoVersionString
        repository_path: http://tendrl.org/repos/gluster_integration/yum/$repo_system_version/
        packages: [tendrl-integration-gluster]
        invocation:
          - type: service
            parameters:
              name: tendrl-gluster-integration.service
              start-action: start
              stop-action: stop
  versions:
    3.x:
      centos:
        =6.x:
          provisioner:
            type: gdeploy
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el6
          integration:
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el6
    4.x:
      centos:
        =6.x:
          provisioner:
            type: gdeploy
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el6
          integration:
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el6
        =7.x:
          provisioner:
            type: gdeploy
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el7
          integration:
            installation:
              type: yum_repository+yum
              parameters:
                repo_system_version: el7
namespace.tendrl.integrations.gluster.provisioner.gdeploy:
  installation_sources:
    yum_repository+yum:
      parameters:
        repo_system_version: namespace.tendrl.platforms.centos.RepoVersionString
      repository_path: http://gdeploy.org/repos/yum/$repo_system_version/
      packages: [gdeploy]
      invocation:
        - type: module
          parameters:
            - module: Tendrl.Provisioning.SetupSsh
              parameters: `tendrl_context.nodes`
"""