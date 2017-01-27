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

1. First install http://github.com/tendrl/commons from the source code::

    $ yum install git python-pip
    $ git clone https://github.com/Tendrl/commons.git
    $ cd commons
    $ pip install virtualenvwrapper
    $ source /usr/bin/virtualenvwrapper.sh
    $ mkvirtualenv node-agent
    $ pip install .

2. Create commons logging config file::

    $ mkdir /etc/tendrl
    $ cp etc/samples/logging.yaml.timedrotation.sample /etc/tendrl/commons_logging.yaml

Note that there are other sample config files for logging shipped with the product
and could be utilized for logging differently. For example there are config files
bundeled for syslog and journald logging as well. These could be used similarly as above.

3. Then install node agent itself::

For installing node agent following dependencies have to be manually installed:

    $ yum install libffi-devel gcc python-devel openssl-devel
    $ yum install -y http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-1.el7.nux.noarch.rpm
    $ yum install hwinfo 

Clone and install the node-agent

    $ git clone https://github.com/Tendrl/node-agent.git
    $ cd node-agent
    $ workon node-agent
    $ pip install .

Note that we use virtualenvwrapper_ here to activate ``node-agent`` `python
virtual enviroment`_. This way, we install *node agent* into the same virtual
enviroment which we have created during installation of *commons*.

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`python virtual enviroment`: https://virtualenv.pypa.io/en/stable/

4. Create config file::

    $ cp etc/logging.yaml.timedrotation.sample /etc/tendrl/node-agent_logging.yaml
    $ cp etc/tendrl/node-agent/node-agent-dev.conf.yaml /etc/tendrl/node-agent/node-agent.conf.yaml

5. Add suitable configuration in config file by updating following lines to
   tendrl configfile(/etc/tendrl/tendrl.conf)::

   etcd_connection = <specify etcd server ip>

6. Create log and conf dirs::

     $ mkdir /var/log/tendrl/commons
     $ mkdir /var/log/tendrl/node-agent/
     $ mkdir /etc/tendrl/node-agent/

7. Run::

    $ tendrl-node-agent

