import click
from clu.command import Command

from lvmscp.exceptions import lvmscpError

from . import parser


@parser.group()
def eng(*args):
    """control the engineering"""
    pass


@eng.command()
@click.argument("message", type=str)
async def lvmieb(command: Command, message):
    """Test the lvmieb"""
    # Check the status (opened / closed) of the shutter
    try:
        lvmieb_status_cmd = await command.actor.send_command("lvmieb", message)
        await lvmieb_status_cmd
    except lvmscpError as err:
        return command.fail(error=str(err))

    if lvmieb_status_cmd.status.did_fail:
        return command.fail(text=lvmieb_status_cmd.status)

    replies = lvmieb_status_cmd.replies
    command.finish(replies[-1].body)


@eng.command()
@click.argument("message", type=str)
async def lvmnps(command: Command, message):
    """Test the lvmnps"""
    # Check the status (opened / closed) of the shutter
    try:
        lvmnps_status_cmd = await command.actor.send_command("lvmnps", message)
        await lvmnps_status_cmd
    except lvmscpError as err:
        return command.fail(error=str(err))

    if lvmnps_status_cmd.status.did_fail:
        return command.fail(text=lvmnps_status_cmd.status)

    replies = lvmnps_status_cmd.replies
    command.finish(replies[-1].body)
