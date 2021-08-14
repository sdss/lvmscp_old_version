# lvmscp

![Versions](https://img.shields.io/badge/python->3.8-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/lvmscp/badge/?version=latest)](https://lvmscp.readthedocs.io/en/latest/?badge=latest)
[![Test](https://github.com/sdss/lvmscp/actions/workflows/test.yml/badge.svg)](https://github.com/sdss/lvmscp/actions/workflows/test.yml)
[![Docker](https://github.com/sdss/lvmscp/actions/workflows/docker.yml/badge.svg)](https://github.com/sdss/lvmscp/actions/workflows/docker.yml)

SDSS-V LVM(Local Volume Mapper) control software for the whole Spectrograpgh system

## Quick Start

### Prerequisite

Install [CLU](https://clu.readthedocs.io/en/latest/) by using PyPI.
```
$ pip install sdss-clu
```

Install [RabbitMQ](https://www.rabbitmq.com/) by using apt-get.

```
$ sudo apt-get install -y erlang
$ sudo apt-get install -y rabbitmq-server
$ sudo systemctl enable rabbitmq-server
$ sudo systemctl start rabbitmq-server
```

Install [pyenv](https://github.com/pyenv/pyenv) by using [pyenv installer](https://github.com/pyenv/pyenv-installer).

```
$ curl https://pyenv.run | bash
```

You should add the code below to `~/.bashrc` by using your preferred editor.
```
# pyenv
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
eval "$(pyenv init --path)"
eval "$(pyenv virtualenv-init -)"
```

### Ping-pong test

Clone this repository.
```
$ git clone https://github.com/sdss/lvmscp
$ cd lvmscp
```

Set the python 3.9.1 virtual environment.
```
$ pyenv install 3.9.1
$ pyenv virtualenv 3.9.1 lvmscp-with-3.9.1
$ pyenv local lvmscp-with-3.9.1
```

Install [poetry](https://python-poetry.org/) and dependencies. For more information, check [sdss/archon](https://github.com/sdss/archon).
```
$ pip install poetry
$ python create_setup.py
$ pip install -e .
```

Start `lvmscp` actor.
```
$ lvmscp start
```

In another terminal, type `clu` and `lvmscp ping` for test.
```
$ clu
lvmscp ping
07:41:22.636 lvmscp > 
07:41:22.645 lvmscp : {
    "text": "Pong."
}
```

Stop `lvmscp` actor.
```
$ lvmscp stop
```
