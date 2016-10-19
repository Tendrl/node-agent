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
