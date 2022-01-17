import click
from clu.command import Command

from lvmscp.actor.supervisor import Supervisor

from . import parser


# from clu.parsers.click import command_parser


@parser.group()
def gage(*args):
    """class of linear gage"""

    pass


@gage.command()
@click.argument(
    "ccd",
    type=click.Choice(["r1", "b1", "z1"]),
    default="z1",
    required=False,
)
async def setccd(command: Command, supervisors: dict[str, Supervisor], ccd: str):
    """Actor command for the user to set which ccd is attatched to the linear gage

    Args:
        command (Command): CLU AMQP Actor command class
        supervisors (dict[str, Supervisor]): the supervisor class of the spectrograph sp1, sp2, sp3
        ccd (str): the string input of which ccd to select [r1, b1, z1] can be selected
    """
    supervisors["sp1"].testccd = ccd
    command.info(text=f"The test CCD for linear gages has changed to {ccd}")
    command.finish()
