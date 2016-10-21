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

1. First install http://github.com/tendrl/bridge_common from the source code::

    $ git clone https://github.com/Tendrl/bridge_common.git
    $ cd bridge_common
    $ mkvirtualenv node_agent
    $ pip install .

2. Then install node agent itself::

    $ git clone https://github.com/Tendrl/node_agent.git
    $ cd node_agent
    $ workon node_agent
    $ pip install .

Note that we use virtualenvwrapper_ here to activate ``node_agent`` `python
virtual enviroment`_. This way, we install *node agent* into the same virtual
enviroment which we have created during installation of *bridge common*.

.. _virtualenvwrapper: https://virtualenvwrapper.readthedocs.io/en/latest/
.. _`python virtual enviroment`: https://virtualenv.pypa.io/en/stable/

3. Add suitable configuration in config file by appending following lines to
   tendrl configfile(/etc/tendrl/tendrl.conf)::
   
   [tendrl_node_agent]
   # Path to log file and log leval
   log_path = /var/log/tendrl/tendrl_node_agent.log
   log_level = DEBUG
   
4. Create log dir::

     $ mkdir /var/log/tendrl
     
5. Run::
     
    $ tendrl-node-agent
