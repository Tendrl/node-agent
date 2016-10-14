===========
Environment
===========

2. Install Etcd>=2.3.x && <3.x (https://github.com/coreos/etcd/releases/tag/v2.3.7)


============
Installation
============

Since there is no stable release yet, the only option is to install the project
from the source.

Development version from the source
-----------------------------------

First install http://github.com/tendrl/bridge_common from the source code::

    $ git clone https://github.com/Tendrl/bridge_common.git
    $ cd bridge_common
    $ mkvirtualenv node_agent
    $ pip install .

Then install node agent itself::

    $ git clone https://github.com/Tendrl/node_agent.git
    $ cd node_agent
    $ workon node_agent
    $ pip install .

Note that we use virtualenvwrapper_ here to activate ``node_agent`` `python
virtual enviroment`_. This way, we install *node agent* into the same virtual
enviroment which we have created during installation of *bridge common*.

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`python virtual enviroment`: https://virtualenv.pypa.io/en/stable/

Installation from source on actual machine
------------------------------------------

1. Install http://github.com/tendrl/bridge_common
2. Install http://github.com/tendrl/node_agent

    At the command line::
    $ git clone http://github.com/tendrl/bridge_common
    $ cd bridge_common
    $ python setup.py install

    $ git clone http://github.com/tendrl/node_agent
    $ cd node_agent
    $ python setup.py install
    

4. Edit /etc/tendrl/tendrl.conf by adding the following lines

   [tendrl_node_agent]
   # Path to log file
   log_path = /var/log/tendrl/tendrl_node_agent.log
   log_level = DEBUG
   
5. mkdir /var/log/tendrl
6. Run
    $ tendrl-node-agent

==========================
Pushing sample job to etcd
==========================

Start etcd server. To push a sample job to etcd job queue, Please run the script create_sample_job.py located at etc directory under node_agent repo. tendrl-node-agent will pick up this job and try to execute it on the node. The response will be updated to the respective job in etcd job queue( http://<etcd-host>:2379/v2/keys/api_job_queue/ ).
