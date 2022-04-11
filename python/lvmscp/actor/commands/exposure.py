#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong YANG (mingyeong@khu.ac.kr)
# @Date: 2021-03-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import logging

import click

from sdsstools import get_logger

from lvmscp.actor.supervisor import Supervisor

from . import parser


# from clu.parsers.click import command_parser


# logging
log = get_logger("sdss-lvmscp")

# lock for exposure lock
exposure_lock = asyncio.Lock()
log.sh.setLevel(logging.DEBUG)


@parser.command()
@click.argument("COUNT", type=int, default=1, required=False)
@click.argument(
    "FLAVOUR",
    type=click.Choice(["bias", "object", "flat", "arc", "dark", "test"]),
    default="object",
    required=False,
)
@click.argument("EXPTIME", type=float, required=False)
@click.argument(
    "spectro",
    type=click.Choice(["sp1", "sp2", "sp3"]),
    default="sp1",
    required=False,
)
@click.argument("BINNING", type=int, default=1, required=False)
@click.argument("HEADER", type=str, default="{}", required=False)
@click.option(
    "--flush",
    "flush",
    default="no",
    required=False,
    help="Flush before the exposure",
)
async def exposure(
    command,
    supervisors: dict[str, Supervisor],
    exptime: float,
    count: int,
    flavour: str,
    spectro: str,
    binning: int,
    flush: str,
    header: str,
):
    """This is the exposure command for running the exposure sequnce.

    Args:
        command ([type]): Command class from clu.actor.Commands
        supervisors (dict[str, Supervisor]): Supervisor class from lvmscp.supervisor.py
        exptime (float): exposure time
        count (int): count of frames
        flavour (str): bias/dark/arc/object type of image
        spectro (str): sp1/sp2/sp3 the spectrograph to take exposure.
        binning (int): binning of the CCD camera
        flush (str): flushing parameter, not required
        header (str): header metadata. The example structure is like such: '\'{"test": 1}\''

    Raises:
        click.UsageError: UsageError for the click class

    Returns:
        [type]: command.finish(filename={array of the files})
    """

    for spectro in supervisors:
        if supervisors[spectro].ready:
            print(supervisors[spectro].name)
            data_directory = await supervisors[spectro].exposure(
                command, exptime, count, flavour, binning, flush, header
            )

    return command.finish(filename=data_directory)
