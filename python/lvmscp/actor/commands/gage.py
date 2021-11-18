import click
from clu.command import Command

from lvmscp.actor.supervisor import Supervisor

from . import parser


@parser.group()
def gage(*args):
    """control the hartmann door."""

    pass


@gage.command()
@click.argument(
    "ccd",
    type=click.Choice(["r1", "b1", "z1"]),
    default="z1",
    required=False,
)
async def setccd(command: Command, supervisors: dict[str, Supervisor], ccd: str):
    """set the CCD to measure gage"""
    supervisors["sp1"].testccd = ccd
    command.info(f"The test CCD for linear gages has changed to {ccd}")
    command.finish()
