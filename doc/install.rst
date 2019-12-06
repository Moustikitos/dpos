.. _install:

=========
 Install
=========

Get the Source Code
-------------------

``dposlib`` is developed on GitHub, where the code is
`always available <https://github.com/Moustikitos/dpos>`_. You can either clone
the public repository::

    $ git clone git://github.com/Moustikitos/dpos.git

You can also download the `zip <https://github.com/Moustikitos/dpos/archive/master.zip>`_.
:mod:`dposlib` will be available if zip file is added as is in python pathes.


Install :mod:`dposlib` using ``pip``
------------------------------------

To install last version of :mod:`dposlib`::

	$ pip install dposlib

To install development vesion::

	$ pip install git+https://github.com/Moustikitos/dpos#egg=dposlib

You may whant to install a specific branch of dposlib::

	$ pip install git+https://github.com/Moustikitos/dpos#egg=dposlib@<branch>

Where ``<branch>`` can be:
  * a commit number
  * a repo branch name
  * a release number


Deploy a multisignature server
------------------------------

It is recommended to use virtual environement::

	$ sudo apt-get install python python-setuptools python-pip virtualenv
	$ mkdir ~/.local/share/ms-server/venv -p
	$ virtualenv ~/.local/share/ms-server/venv -q
	$ cd ~
    $ git clone https://github.com/Moustikitos/
	$ . ~/.local/share/ms-server/venv/bin/activate
    $ pip install -r ~/dpos/requirements.txt

Once ``dpos`` repository cloned, there is no need to install dposlib because 
python pathes are set accordingly.

Deploy using ``flask`` server::

	$ . ~/.local/share/ms-server/venv/bin/activate
	$ export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
	$ python ~/dpos/mssrv/srv.py

Deploy using ``gunicorn`` server::

	$ . ~/.local/share/ms-server/venv/bin/activate
	$ export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
	$ gunicorn --bind=0.0.0.0:5000 --workers=5 mssrv.app:app

If you have ``pm2`` installed you can start ``flask`` or ``gunicorn`` server::

	$ rem flask server
	$ pm2 start ~/dpos/srv.json
	$ rem gunicorn server
	$ pm2 start ~/dpos/app.json
