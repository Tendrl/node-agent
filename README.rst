Tendrl node agent resides on every node managed by tendlr. It is
responsible for operating system level operations such as hardware
inventory, service management, process monitoring etc. The node agent
also serves as the provisioning controller and can invoke provisioning
operations on the node.

-  Free software: LGPL2

-  Documentation:
   https://github.com/Tendrl/node_agent/tree/master/doc/source

-  Source: https://github.com/Tendrl/node_agent

-  Bugs: https://github.com/Tendrl/node_agent/issues

|Build status| |Coverage|

Features
========

-  Provide Node hardware inventory (cpu, memory, processes etc) details
   in central store.

-  Implements operations Ceph/Gluster cluster import .

Installation from Source on CentOS 7
====================================

    **Important**

    Node agent needs to be installed on every node of the storage
    cluster that is to be managed by tendrl.

    **Note**

    All the commands are run as a regular user that has ``sudo``
    privileges. The commands are all assumed to be run from a single
    directory, which by default could be the user’s home directory. If
    different, the required current directory is indicated in ``[]``
    before the shell prompt ``$``.

Deployment Requirements
-----------------------

1. Ensure that etcd is running on a node in the network and is reachable
   from the node you’re about to install the node agent on. Note it’s
   address and port.

System Setup
------------

1. Install the build toolchain and other development packages.

   ::

       $ sudo yum groupinstall 'Development Tools'
       $ sudo yum install libffi-devel openssl-devel

2. Install
   `virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/>`__.

   ::

       $ sudo yum install python-virtualenv python-virtualenvwrapper python-devel pip

3. Create system directories.

   ::

       $ sudo mkdir -p /etc/tendrl/node_agent \
         /etc/tendrl/{ceph,gluster}_integration \
         /var/log/tendrl/node_agent \
         /var/log/tendrl/common \
         /var/log/tendrl/{ceph,gluster}_integration

Environment Setup
-----------------

1. Configure ``virtualenvwrapper``.

   Setup the shell startup files based on the ``virtualenvwrapper``
   documentation at:
   https://virtualenvwrapper.readthedocs.io/en/latest/install.html#shell-startup-file

   Be sure to adjust the value of ``source`` to the output of:

   ::

       $ which virtualenvwrapper.sh # Should be /usr/bin/virtualenvwrapper.sh

2. Create and load the virtual environment for the node agent.

   ::

       $ mkvirtualenv tendrl-node-agent
       $ workon tendrl-node-agent

Install Tendrl common and node\_agent
-------------------------------------

1. Install the `common library <https://github.com/Tendrl/common>`__.

   ::

       $ git clone https://github.com/Tendrl/common.git common
       $ pushd common
       [common] $ workon tendrl-node-agent
       [common] $ pip install .
       [common] $ popd

2. Install the node agent.

   ::

       $ git clone https://github.com/Tendrl/node_agent.git
       $ pushd node_agent
       [node_agent] $ workon tendrl-node-agent
       [node_agent] $ pip install .
       [node_agent] $ popd

3. Fetch the ceph\_integration and gluster\_integration codebases.

   ::

       $ git clone https://github.com/Tendrl/ceph_integration.git
       $ git clone https://github.com/Tendrl/gluster_integration.git

Configuration
-------------

1. Create the tendrl configuration file ``/etc/tendrl/tendrl.conf``.

   ::

       $ cp common/etc/tendrl/tendrl.conf.sample /etc/tendrl/tendrl.conf

   a. Configure the following ``etcd_port`` and ``etcd_connection``
      directives in ``/etc/tendrl/tendrl.conf`` to point to the etcd
      instance discussed in the first step.

2. Install the common logging configuration file
   ``/etc/tendrl/common_logging.yaml``.

   ::

       $ cp common/etc/samples/logging.yaml.timedrotation.sample \
         /etc/tendrl/common_logging.yaml

    **Note**

    There are other sample configuration files in the
    ``common/etc/samples`` directory which could be used to setup
    logging for different system configuration such as via syslog and
    journald.

1. Install the node agent logging configuration file
   ``/etc/tendrl/node_agent_logging.yaml``.

   ::

       $ cp node_agent/etc/logging.yaml.timedrotation.sample \
         /etc/tendrl/node_agent_logging.yaml
       $ cp ceph_integration/etc/logging.yaml.timedrotation.sample \
         /etc/tendrl/ceph_integration_logging.yaml
       $ cp gluster_integration/etc/logging.yaml.timedrotation.sample \
         /etc/tendrl/gluster_integration_logging.yaml

    **Note**

    There are other sample configuration files in the ``node_agent/etc``
    directory which could be used to setup logging for different system
    configuration such as via syslog and journald.

1. Append the following configuration to the tendrl configuration file
   ``/etc/tendrl/tendrl.conf``:

   ::

       [node_agent]
       # Path to the log file and log level
       log_cfg_path = /etc/tendrl/node_agent_logging.yaml
       log_level = DEBUG
       tendrl_exe_file_prefix = /tmp/.tendrl_runner

Run
---

::

    $ workon tendrl-node-agent
    $ tendrl-node-agent

Developer documentation
=======================

There’s additional sphinx documentation in ``docs/source``. To build it,
run:

::

    $ python setup.py build_sphinx

.. |Build status| image:: https://travis-ci.org/Tendrl/node_agent.svg?branch=master
.. |Coverage| image:: https://coveralls.io/repos/github/Tendrl/node_agent/badge.svg?branch=master

