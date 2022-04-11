import click

from lvmscp.actor.supervisor import Supervisor

from . import parser


# from clu.parsers.click import command_parser


@parser.group()
def hartmann(*args):
    """control the hartmann door."""

    pass


@hartmann.command()
@click.argument(
    "request",
    type=click.Choice(["right", "left", "both", "close"]),
    required=True,
)
@click.argument(
    "spectro",
    type=click.Choice(["sp1", "sp2", "sp3"]),
    default="sp1",
    required=False,
)
async def set(command, supervisors: dict[str, Supervisor], request: str, spectro: str):
    """The Actor command to set the hartmann door on fixed positions, such as
    left hartmann door opened only, right hartmann door opened only,
    both hartmann doors opened, and both hartmann doors closed

    Args:
        command ([type]): The CLU AMQP Command class
        supervisors (dict[str, Supervisor]): supervisor instance of each
        spectrograph sp1, sp2, sp3 is the element of the dictionary.
        request (str): request of which door position that the user want
        spectro (str): the spectrograph that should be choosen

    Returns:
        [type]: command.finish()
    """
    for spectro in supervisors:
        if supervisors[spectro].ready:
            await supervisors[spectro].SetHartmann(command, request)
            command.info(
                hartmann={
                    "hartmann_left": supervisors[spectro].hartmann_left_status,
                    "hartmann_right": supervisors[spectro].hartmann_right_status,
                }
            )

    return command.finish()


@hartmann.command()
async def init(command, supervisors: dict[str, Supervisor], request: str, spectro: str):
    """Write the command for turning on the hartmann doors and initialize both"""

    for spectro in supervisors:
        if supervisors[spectro].ready:
            await supervisors[spectro].SetHartmann(command, request)
            command.info(
                hartmann={
                    "hartmann_left": supervisors[spectro].hartmann_left_status,
                    "hartmann_right": supervisors[spectro].hartmann_right_status,
                }
            )

    return command.finish()
