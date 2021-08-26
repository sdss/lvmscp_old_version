lvmnps
======

|Versions| |Documentation Status| |Test| |Docker| 

SDSS-V LVM(Local Volume Mapper) control software for the whole Spectrograpgh system

Quick Start
-----------

Prerequisite
~~~~~~~~~~~~

Install `CLU <https://clu.readthedocs.io/en/latest/>`__ by using PyPI.

::

    $ pip install sdss-clu

Install `RabbitMQ <https://www.rabbitmq.com/>`__ by using apt-get.

::

    $ sudo apt-get install -y erlang
    $ sudo apt-get install -y rabbitmq-server
    $ sudo systemctl enable rabbitmq-server
    $ sudo systemctl start rabbitmq-server

Install `pyenv <https://github.com/pyenv/pyenv>`__ by using `pyenv
installer <https://github.com/pyenv/pyenv-installer>`__.

::

    $ curl https://pyenv.run | bash

You should add the code below to ``~/.bashrc`` by using your preferred
editor.

::

    # pyenv
    export PYENV_ROOT="$HOME/.pyenv"
    export PATH="$PYENV_ROOT/bin:$PATH"
    eval "$(pyenv init -)"
    eval "$(pyenv init --path)"
    eval "$(pyenv virtualenv-init -)"

``pyenv`` builds Python from source. So you should install build
dependencies. For more information, check `Common build
problems <https://github.com/pyenv/pyenv/wiki/Common-build-problems>`__.

::

    $ sudo apt-get install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl

Clone this repository.
::

    $ git clone https://github.com/sdss/lvmscp
    $ cd lvmscp


Set the python 3.9.1 virtual environment.

::

    $ pyenv install 3.9.1
    $ pyenv virtualenv 3.9.1 lvmscp-with-3.9.1
    $ pyenv local lvmscp-with-3.9.1

Install `poetry <https://python-poetry.org/>`__ and dependencies. For
more information, check
`sdss/archon <https://github.com/sdss/archon>`__.

::

    $ pip install poetry
    $ python create_setup.py
    $ pip install -e .

Start the actor
~~~~~~~~~~~~~~~

Start ``lvmscp`` actor inside your virtualenv directory.

::

    $ lvmscp start

In another terminal, type ``clu`` and ``lvmscp ping`` for test.

::

    $ clu
    lvmscp ping
         07:41:22.636 lvmscp > 
         07:41:22.645 lvmscp : {
             "text": "Pong."
             }

Stop ``lvmscp`` actor.

::

    $ lvmscp stop


.. |Versions| image:: https://img.shields.io/badge/python->3.8-blue
.. |Documentation Status| image:: https://readthedocs.org/projects/lvmscp/badge/?version=latest
   :target: https://lvmscp.readthedocs.io/en/latest/?badge=latest
.. |Test| image:: https://github.com/sdss/lvmscp/actions/workflows/test.yml/badge.svg
   :target: https://github.com/sdss/lvmscp/actions/workflows/test.yml
.. |Docker| image:: https://github.com/sdss/lvmscp/actions/workflows/Docker.yml/badge.svg
   :target: https://github.com/sdss/lvmscp/actions/workflows/Docker.yml