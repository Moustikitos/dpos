.. _install:

=========
 Install
=========

``pip``
-------

To install ``dposlib`` on your system, simply type the ``pip`` command line::

	$ pip install dposlib

If you whant to install a specific branch of dposlib using ``pip``::

	$ pip install git+https://github.com/Moustikitos/dpos#egg=dposlib@<branch>

Where ``<branch>`` can be:
  * a commit number
  * a repo branch name
  * a release number

Get the Source Code
-------------------

``dposlib`` is developed on GitHub, where the code is
`always available <https://github.com/Moustikitos/dpos>`_.

You can either clone the public repository::

    $ git clone git://github.com/Moustikitos/dpos.git

Or, download the `zip <https://github.com/Moustikitos/dpos/archive/master.zip>`_::

    $ curl -OL https://github.com/psf/requests/tarball/master
    # optionally, zipball is also available (for Windows users).

Once you have a copy of the source, you can embed it in your own Python
package, or install it into your site-packages easily::

    $ cd requests
    $ pip install .
