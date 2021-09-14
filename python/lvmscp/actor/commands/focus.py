import logging

import click

from sdsstools import get_logger

from lvmscp.exceptions import lvmscpError

#  import asyncio
from . import parser


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
async def focus(command, exptime: float, count: int, spectro: str):
    """command for focusing sequence"""

    final_data = {}

    # Check if lamp is on
    log.debug("Checking flat lamps . . .")
    command.info(text="Checking flat lamps . . .")
    try:
        lamps_on = await check_flat_lamp(command)
        for key, value in lamps_on.items():
            log.info("{key} arc lamps on!")
            command.info(text=f"{key} arc lamps on!")
    except lvmscpError as err:
        log.error(err)
        return command.fail(text=err)

    final_data.update(lamps_on)

    # Loop for counts
    # start exposure loop
    for nn in range(count):

        #   set the hartmann door - left
        command.info("hartmann left setting . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"hartmann set left {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return "Failed to receive the status of the lvmscp"
        else:
            replies = scp_status_cmd.replies
            command.info(replies.body[-1])
            final_data.update(replies.body[-1])

        # developing the focus command fluid code 2021/09/11 Changgon Kim
        # have to output the data file saved for each lamps, adding the hartmann information

        #   Take the flat image
        command.info("arc image taking . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 flat {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return "Failed to receive the status of the lvmscp"
        else:
            replies = scp_status_cmd.replies
            command.info(
                {
                    "z1_arc": replies.body[-2].body["filename"],
                    "b1_arc": replies.body[-4].body["filename"],
                    "r1_arc": replies.body[-6].body["filename"],
                }
            )

            final_data.update(
                {
                    "z1_arc": replies.body[-2].body["filename"],
                    "b1_arc": replies.body[-4].body["filename"],
                    "r1_arc": replies.body[-6].body["filename"],
                }
            )

        #   take the dark image
        command.info("dark image taking . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 dark {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return "Failed to receive the status of the lvmscp"
        else:
            replies = scp_status_cmd.replies
            command.info(
                {
                    "z1_dark": replies.body[-2].body["filename"],
                    "b1_dark": replies.body[-4].body["filename"],
                    "r1_dark": replies.body[-6].body["filename"],
                }
            )

            final_data.update(
                {
                    "z1_dark": replies.body[-2].body["filename"],
                    "b1_dark": replies.body[-4].body["filename"],
                    "r1_dark": replies.body[-6].body["filename"],
                }
            )

        #   set the hartmann door - right
        command.info("hartmann right setting . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"hartmann set right {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return "Failed to receive the status of the lvmscp"
        else:
            replies = scp_status_cmd.replies
            command.info(replies.body[-1])
            final_data.update(replies.body[-1])

        #   Take the flat image
        command.info("arc image taking . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 flat {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return "Failed to receive the status of the lvmscp"
        else:
            replies = scp_status_cmd.replies
            command.info(
                {
                    "z1_arc": replies.body[-2].body["filename"],
                    "b1_arc": replies.body[-4].body["filename"],
                    "r1_arc": replies.body[-6].body["filename"],
                }
            )
            final_data.update(
                {
                    "z1_arc": replies.body[-2].body["filename"],
                    "b1_arc": replies.body[-4].body["filename"],
                    "r1_arc": replies.body[-6].body["filename"],
                }
            )

        #   take the dark image
        command.info("dark image taking . . .")
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 dark {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return "Failed to receive the status of the lvmscp"
        else:
            replies = scp_status_cmd.replies
            command.info(
                {
                    "z1_dark": replies.body[-2].body["filename"],
                    "b1_dark": replies.body[-4].body["filename"],
                    "r1_dark": replies.body[-6].body["filename"],
                }
            )

            final_data.update(
                {
                    "z1_dark": replies.body[-2].body["filename"],
                    "b1_dark": replies.body[-4].body["filename"],
                    "r1_dark": replies.body[-6].body["filename"],
                }
            )

    # information of the saved files
    command.info(final_data)

    command.finish()


async def check_flat_lamp(command):
    """Check the flat lamp status"""

    flat_lamp_cmd = await (await command.actor.send_command("lvmnps", "status all"))
    if flat_lamp_cmd.status.did_fail:
        return "Failed getting status from the network power switch"
    else:
        replies = flat_lamp_cmd.replies

        check_lamp = {
            "Argon": replies[-2].body["STATUS"]["DLI-NPS-03"]["Argon"]["STATE"],
            "Xenon": replies[-2].body["STATUS"]["DLI-NPS-03"]["Xenon"]["STATE"],
            "HgAr": replies[-2].body["STATUS"]["DLI-NPS-03"]["Hg (Ar)"]["STATE"],
            "LDLS": replies[-2].body["STATUS"]["DLI-NPS-03"]["LDLS"]["STATE"],
            "Krypton": replies[-2].body["STATUS"]["DLI-NPS-03"]["Krypton"]["STATE"],
            "Neon": replies[-2].body["STATUS"]["DLI-NPS-03"]["Neon"]["STATE"],
            "HgNe": replies[-2].body["STATUS"]["DLI-NPS-03"]["Hg (Ne)"]["STATE"],
        }

        sum = 0
        lamp_on = {}

        for key, value in check_lamp.items():
            sum = sum + value
            if value == 1:
                command.info(text=f"{key} flat lamp is on!")
                lamp_on.update(key="ON")

        return lamp_on
