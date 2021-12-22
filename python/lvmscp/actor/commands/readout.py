import click
from clu.command import Command

from lvmscp.actor.supervisor import Supervisor
from lvmscp.exceptions import lvmscpError

from . import parser


@parser.command()
@click.argument(
    "readout",
    type=click.Choice(["400", "800", "HDR"]),
    required=True,
)
async def readout(command: Command, supervisors: dict[str, Supervisor], readout: str):

    if readout == "400":
        try:
            archon_status_cmd = await command.actor.send_command(
                "archon", "init lvm/config/archon/LVM_400MHz.acf"
            )
            await archon_status_cmd
        except lvmscpError as err:
            return command.fail(error=str(err))
    elif readout == "800":
        try:
            archon_status_cmd = await command.actor.send_command(
                "archon", "init lvm/config/archon/LVM_800MHz.acf"
            )
            await archon_status_cmd
        except lvmscpError as err:
            return command.fail(error=str(err))
    elif readout == "HDR":
        try:
            archon_status_cmd = await command.actor.send_command("archon", "init --hdr")
            await archon_status_cmd
        except lvmscpError as err:
            return command.fail(error=str(err))

    if archon_status_cmd.status.did_fail:
        return command.fail(text=archon_status_cmd.status)

    if readout == "400" or readout == "800":
        command.info(text=f"The readout mode is set to {readout}mHz")
    else:
        command.info(text=f"The {readout} mode was set. (32-bit Sampling)")

    return command.finish()
