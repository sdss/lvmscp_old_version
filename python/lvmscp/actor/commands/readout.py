import click
from clu.command import Command

from lvmscp.actor.supervisor import Supervisor

from . import parser


@parser.command()
@click.argument(
    "readout",
    type=click.Choice(["400", "800", "HDR"]),
    required=True,
)
async def readout(command: Command, supervisors: dict[str, Supervisor], readout: str):
    """The Actor command to set the readout mode of the CCD.
    It sends the 'archon init {acf_file}' command to the archon actor.

    Args:
        command (Command): CLU AMQP command class
        supervisors (dict[str, Supervisor]): supervisor instance of each
        spectrograph sp1, sp2, sp3 readout (str): readout mode that the
        user want to set [400Mhz, 800Mhz, HDR] corresponds to [400, 800, HDR]

    Returns:
        [type]: command.finish()
    """

    for spectro in supervisors:
        if supervisors[spectro].ready:
            await supervisors[spectro].SetReadout(command, readout)

    if readout == "400" or readout == "800":
        command.info(text=f"The readout mode is set to {readout}mHz")
    else:
        command.info(text=f"The {readout} mode was set. (32-bit Sampling)")

    return command.finish()
