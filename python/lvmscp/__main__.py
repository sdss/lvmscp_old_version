# encoding: utf-8
#
# added by CK 2021/04/06

# -*- coding: utf-8 -*-
#
# @Date: 2020-10-26
# @Filename: __main__.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import os

import click
from click_default_group import DefaultGroup
from clu.tools import cli_coro as cli_coro_lvmscp

from sdsstools.daemonizer import DaemonGroup

from lvmscp.actor.actor import lvmscp as SCPActorInstance


@click.group(cls=DefaultGroup, default="actor", default_if_no_args=True)
@click.option(
    "-c",
    "--config",
    "config_file",
    type=click.Path(exists=True, dir_okay=False),
    help="Path to the user configuration file.",
)
@click.option(
    "-v",
    "--verbose",
    count=True,
    help="Debug mode. Use additional v for more details.",
)
@click.pass_context
def lvmscp(ctx, config_file, verbose):
    """brings the configuration .yaml file"""

    ctx.obj = {"verbose": verbose, "config_file": config_file}


@lvmscp.group(cls=DaemonGroup, prog="scp_actor", workdir=os.getcwd())
@click.pass_context
@cli_coro_lvmscp
async def actor(ctx):
    """Runs the actor."""
    default_config_file = os.path.join(os.path.dirname(__file__), "etc/lvmscp.yml")

    lvmscp_obj = SCPActorInstance.from_config(default_config_file)

    await lvmscp_obj.start()
    await lvmscp_obj.run_forever()


if __name__ == "__main__":
    lvmscp()
