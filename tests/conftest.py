# encoding: utf-8
#
# conftest.py

"""
Here you can add fixtures that will be used for all the tests in this
directory. You can also add conftest.py files in underlying subdirectories.
Those conftest.py will only be applies to the tests in that subdirectory and
underlying directories. See https://docs.pytest.org/en/2.7.3/plugins.html for
more information.
"""

import os

import clu.testing
import pytest as pytest
from clu import LegacyActor
from clu.actor import AMQPBaseActor

from sdsstools import merge_config, read_yaml_file

from lvmscp import config
from lvmscp.actor.actor import lvmscp as ScpActor


@pytest.fixture()
def test_config():

    extra = read_yaml_file(os.path.join(os.path.dirname(__file__), "test_actor.yml"))
    yield merge_config(extra, config)


@pytest.fixture()
async def actor(test_config: dict, mocker):

    # We need to call the actor .start() method to force it to create the
    # supervisors and to start the tasks, but we don't want to run .start()
    # on the actor.

    mocker.patch.object(AMQPBaseActor, "start")

    _actor = ScpActor.from_config(test_config)

    await _actor.start()

    _actor = await clu.testing.setup_test_actor(_actor)  # type: ignore

    yield _actor

    _actor.mock_replies.clear()
    await _actor.stop()


@pytest.fixture()
def test_config_lvmieb():

    extra = read_yaml_file(os.path.join(os.path.dirname(__file__), "test_lvmieb.yml"))
    yield merge_config(extra, config)


@pytest.fixture()
async def lvmieb(test_config_lvmieb: dict, mocker):

    # We need to call the actor .start() method to force it to create the
    # supervisors and to start the tasks, but we don't want to run .start()
    # on the actor.

    mocker.patch.object(AMQPBaseActor, "start")

    _actor = await clu.testing.setup_test_actor(
        LegacyActor("lvmieb", host="localhost", port=5672)
    )  # type: ignore

    yield _actor
    await _actor.start()

    # _actor.mock_replies.clear()
    await _actor.stop()
