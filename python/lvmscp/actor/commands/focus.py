import logging

import click

from sdsstools import get_logger

from lvmscp.actor.supervisor import Supervisor
from lvmscp.exceptions import lvmscpError

#  import asyncio
from . import parser


# from clu.parsers.click import command_parser

# logging
log = get_logger("sdss-lvmscp")

# lock for exposure lock
log.sh.setLevel(logging.DEBUG)


@parser.command()
@click.argument("COUNT", type=int, default=1, required=False)
@click.argument("EXPTIME", type=float, required=False)
@click.argument(
    "spectro",
    type=click.Choice(["sp1", "sp2", "sp3"]),
    default="sp1",
    required=False,
)
@click.option(
    "--dark",
    flag_value=True,
    type=bool,
    required=False,
    default=False,
    help="Option for taking dark",
)
async def focus(
    command,
    supervisors: dict[str, Supervisor],
    exptime: float,
    count: int,
    spectro: str,
    dark: bool,
):
    """command taking the focus sequence for taking arc lamp frame with each hartmann door open/close

    Args:
        command ([type]): [description]
        supervisors (dict[str, Supervisor]): [description]
        exptime (float): [description]
        count (int): [description]
        spectro (str): [description]
        dark (bool): [description]

    Returns:
        command.finish(focus=dict)
    """

    final_data = {}
    # 47 is readout seconds when readout mode is 800Mhz. need to change this by each readout mode..
    if dark:
        integ_time = (exptime + 47) * 3
    else:
        integ_time = (exptime + 47) * 2

    command.info(text=f"Total exposure time will be = {integ_time}")
    # Check if lamp is on
    log.debug("Checking arc lamps . . .")
    command.info(text="Checking arc lamps . . .")
    try:
        lamps_on = await check_arc_lamp(command)
    except lvmscpError as err:
        log.error(err)
        return command.fail(text=err)
    if lamps_on:
        final_data.update(lamps_on)
    elif not lamps_on:
        return command.fail(text="Flat lamps are not on . . . ")

    # Loop for counts
    # start exposure loop
    for nn in range(count):

        #   set the hartmann door - left
        command.info(text="hartmann left setting . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"hartmann set left {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(reply=replies[-2].body)
            final_data.update(replies[-2].body)

        #   Take the arc image
        command.info(text="arc image taking . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 arc {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(
                reply={
                    "z1_arc": replies[-1].body["filename"][0],
                    "b1_arc": replies[-1].body["filename"][1],
                    "r1_arc": replies[-1].body["filename"][2],
                }
            )

            final_data.update(
                {
                    "LEFT_ARC": {
                        "z1_arc": replies[-1].body["filename"][0],
                        "b1_arc": replies[-1].body["filename"][1],
                        "r1_arc": replies[-1].body["filename"][2],
                    }
                }
            )

        #   set the hartmann door - right
        command.info(text="hartmann right setting . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"hartmann set right {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(reply=replies[-2].body)
            final_data.update(replies[-2].body)

        #   Take the arc image
        command.info(text="arc image taking . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 arc {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(
                reply={
                    "z1_arc": replies[-1].body["filename"][0],
                    "b1_arc": replies[-1].body["filename"][1],
                    "r1_arc": replies[-1].body["filename"][2],
                }
            )
            final_data.update(
                {
                    "RIGHT_ARC": {
                        "z1_arc": replies[-1].body["filename"][0],
                        "b1_arc": replies[-1].body["filename"][1],
                        "r1_arc": replies[-1].body["filename"][2],
                    }
                }
            )

        if dark:
            #  take the dark image
            command.info(text="dark image taking . . .")
            scp_status_cmd = await command.actor.send_command(
                "lvmscp", f"exposure 1 dark {exptime} {spectro}"
            )
            await scp_status_cmd

            if scp_status_cmd.status.did_fail:
                return command.fail(text="Failed to receive the status of the lvmscp")
            else:
                replies = scp_status_cmd.replies
                command.info(
                    reply={
                        "z1_dark": replies[-2].body["reply"]["filename"],
                        "b1_dark": replies[-4].body["reply"]["filename"],
                        "r1_dark": replies[-6].body["reply"]["filename"],
                    }
                )

                final_data.update(
                    {
                        "DARK": {
                            "z1_dark": replies[-2].body["reply"]["filename"],
                            "b1_dark": replies[-4].body["reply"]["filename"],
                            "r1_dark": replies[-6].body["reply"]["filename"],
                        }
                    }
                )

    # information of the saved files
    return command.finish(focus=final_data)


async def check_arc_lamp(command):
    """Check the arc lamp status

    Args:
        command ([type]): [description]

    Returns:
        [type]: [description]
    """

    arc_lamp_cmd = await (await command.actor.send_command("lvmnps", "status"))
    if arc_lamp_cmd.status.did_fail:
        return False
    else:
        replies = arc_lamp_cmd.replies

        check_lamp = {
            "625NM": replies[-2].body["status"]["DLI-01"]["625 nm LED (M625L4)"][
                "state"
            ],
            "ARGON": replies[-2].body["status"]["DLI-03"]["Argon"]["state"],
            "XENON": replies[-2].body["status"]["DLI-03"]["Xenon"]["state"],
            "HGAR": replies[-2].body["status"]["DLI-03"]["Hg (Ar)"]["state"],
            "LDLS": replies[-2].body["status"]["DLI-03"]["LDLS"]["state"],
            "KRYPTON": replies[-2].body["status"]["DLI-03"]["Krypton"]["state"],
            "NEON": replies[-2].body["status"]["DLI-03"]["Neon"]["state"],
            "HGNE": replies[-2].body["status"]["DLI-03"]["Hg (Ne)"]["state"],
        }

        sum = 0
        lamp_on = {}

        for key, value in check_lamp.items():
            sum = sum + value
            if value == 1:
                command.info(text=f"{key} arc lamp is on!")

        if sum > 0:
            lamp_on.update(check_lamp)
            return lamp_on
        elif sum == 0:
            return False


def pretty(time):
    """Function for logging

    Args:
        time ([type]): datetime.datetime.now() is general input

    Returns:
        [type]: change the color for logging
    """
    return f"{bcolors.OKCYAN}{bcolors.BOLD}{time}{bcolors.ENDC}"


def pretty2(time):
    """Function for logging

    Args:
        time ([type]): datetime.datetime.now() is general input

    Returns:
        [type]: change the color for logging
    """
    return f"{bcolors.WARNING}{bcolors.BOLD}{time}{bcolors.ENDC}"


class bcolors:
    """structure class for color values."""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
