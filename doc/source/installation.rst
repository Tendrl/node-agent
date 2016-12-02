===========
Environment
===========

1. Install Etcd>=2.3.x && <3.x (https://github.com/coreos/etcd/releases/tag/v2.3.7)


============
Installation
============

Since there is no stable release yet, the only option is to install the project
from the source.

Development version from the source
-----------------------------------

1. First install http://github.com/tendrl/common from the source code::

    $ git clone https://github.com/Tendrl/common.git
    $ cd common
    $ mkvirtualenv node_agent
    $ pip install .

2. Create common logging config file::

    $ cp etc/samples/logging.yaml.timedrotation.sample /etc/tendrl/common_logging.yaml

Note that there are other sample config files for logging shipped with the product
and could be utilized for logging differently. For example there are config files
bundeled for syslog and journald logging as well. These could be used similarly as above.

3. Then install node agent itself::

For installing node agent following dependencies have to be manually installed:

    $ yum install libffi-devel gcc python-devel openssl-devel

Clone and install the node-agent

    $ git clone https://github.com/Tendrl/node_agent.git
    $ cd node_agent
    $ workon node_agent
    $ pip install .

One of the dependency of node-agent needs a higher version of setuptools, So user
has to manually upgrade the setuptools package to alteast setuptools>=11.3

    $ pip install setuptools --upgrade

Note that we use virtualenvwrapper_ here to activate ``node_agent`` `python
virtual enviroment`_. This way, we install *node agent* into the same virtual
enviroment which we have created during installation of *common*.

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`python virtual enviroment`: https://virtualenv.pypa.io/en/stable/

4. Create config file::

    $ cp etc/logging.yaml.timedrotation.sample /etc/tendrl/node_agent_logging.yaml
    $ cp etc/tendrl/tendrl.conf.sample /etc/tendrl/tendrl.conf

4. Add suitable configuration in config file by modifying following lines in
   tendrl configfile(/etc/tendrl/tendrl.conf) if required::

   [node_agent]
   # Path to log file and log leval
   log_cfg_path = /etc/tendrl/node_agent_logging.yaml
   log_level = DEBUG
   tendrl_exe_file_prefix = /tmp/.tendrl_runner

4. Create log and conf dirs::

     $ mkdir /var/log/tendrl/common
     $ mkdir /var/log/tendrl/node_agent/
     $ mkdir /etc/tendrl/node_agent/

5. Run::

    $ tendrl-node-agent
