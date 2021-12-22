import click
from clu.command import Command

from lvmscp.actor.supervisor import Supervisor
from lvmscp.exceptions import lvmscpError

from . import parser


# from clu.parsers.click import command_parser


@parser.group()
def talk(*args):
    """talk to lower actors for engineering"""
    pass


@talk.command()
@click.argument("message", type=str)
async def lvmieb(command: Command, supervisors: dict[str, Supervisor], message):
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
    command.finish(reply=replies[-2].body)


@talk.command()
@click.argument("message", type=str)
async def lvmnps(command: Command, supervisors: dict[str, Supervisor], message):
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
    command.finish(reply=replies[-2].body)
