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

Install developpement version::

    $ bash <(curl -s https://raw.githubusercontent.com/Moustikitos/dpos/master/bash/mssrv-install.sh)

Once ``dpos`` repository cloned, there is no need to install dposlib because 
python pathes are set accordingly.

Deploy using ``flask`` server::

    $ . ~/.local/share/ms-server/venv/bin/activate
    $ export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
    $ python ~/dpos/mssrv/srv.py

Deploy using ``gunicorn`` server::

    $ . ~/.local/share/ms-server/venv/bin/activate
    $ export PYTHONPATH=${PYTHONPATH}:${HOME}/dpos
    $ gunicorn --bind=0.0.0.0:5050 --workers=5 mssrv:app

Deploy using ``ms`` command::

    $ # activate virtual environment
    $ bash ~/dpos/bash/activate
    $ ./ms --help
    $ Usage:
    $    ms start-api [-p <api-port>]
    $    ms start-app [-p <port> -s <server>]
    $    ms (restart-api | restart-app | stop-api | stop-app)
    $    ms (log-api | log-app)
    $ 
    $ Options:
    $ -p --port=<port>       : the port to use [default: 5050]
    $ -s --server=<server>   : the ms-api server to link to [default: http://127.0.0.1:5050]
    $ 
    $ Subcommands:
    $    start-api     : start multi signature server
    $    start-app     : start multi signature app
    $    restart-app/api : restart multi signature api/app
    $    stop-api/app  : stop multi signature server/app
    $    log-api/app   : show multi signature server/app logs
