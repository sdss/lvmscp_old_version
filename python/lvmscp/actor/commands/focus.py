import logging

import click

from sdsstools import get_logger

from lvmscp.actor.supervisor import Supervisor
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
    """command for focusing sequence"""

    final_data = {}
    # 47 is readout seconds
    if dark:
        integ_time = (exptime + 47) * 3
    else:
        integ_time = (exptime + 47) * 2

    command.info(f"Total exposure time will be = {integ_time} sec")
    # Check if lamp is on
    log.debug("Checking arc lamps . . .")
    command.info(text="Checking arc lamps . . .")
    try:
        lamps_on = await check_flat_lamp(command)
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
        command.info("hartmann left setting . . .")

        hartmann_status_cmd = await command.actor.send_command(
            "lvmieb", f"hartmann status {spectro}"
        )
        await hartmann_status_cmd

        if hartmann_status_cmd.status.did_fail:
            return "Failed to receive the status of the hartmann status"
        else:
            replies = hartmann_status_cmd.replies
            hartmann_left_status = replies[-2].body[spectro]["hartmann_left"]
            hartmann_right_status = replies[-2].body[spectro]["hartmann_right"]

        request = "left"
        
        # Makes the status only the right door opened
        if request == "left":
            if hartmann_left_status == "closed":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann open {spectro} --side={request}"
                )
                await open_cmd
            elif hartmann_left_status == "opened":
                command.info(text=f"{request} already opened")

            if hartmann_right_status == "opened":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann close {spectro} --side=right"
                )
                await open_cmd

        """
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"hartmann set left {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(replies[-2].body)
            final_data.update(replies[-2].body)

        # developing the focus command fluid code 2021/09/11 Changgon Kim
        # have to output the data file saved for each lamps, adding the hartmann information
        """
        
        #   Take the arc image

        
        """
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 flat {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(
                {
                    "z1_arc": replies[-2].body["filename"],
                    "b1_arc": replies[-4].body["filename"],
                    "r1_arc": replies[-6].body["filename"],
                }
            )

            final_data.update(
                {
                    "LEFT_ARC": {
                        "z1_arc": replies[-2].body["filename"],
                        "b1_arc": replies[-4].body["filename"],
                        "r1_arc": replies[-6].body["filename"],
                    }
                }
            )
        """
        
        #   set the hartmann door - right
        command.info("hartmann right setting . . .")
        request = "right"
        
        if request == "right":
            if hartmann_right_status == "closed":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann open {spectro} --side={request}"
                )
                await open_cmd
            elif hartmann_right_status == "opened":
                command.info(text=f"{request} already opened")

            if hartmann_left_status == "opened":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann close {spectro} --side=left"
                )
                await open_cmd
        
        """
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"hartmann set right {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(replies[-2].body)
            final_data.update(replies[-2].body)
        """
        
        #   Take the arc image
        command.info("arc image taking . . .")
        
        """
        scp_status_cmd = await command.actor.send_command(
            "lvmscp", f"exposure 1 flat {exptime} {spectro}"
        )
        await scp_status_cmd

        if scp_status_cmd.status.did_fail:
            return command.error("Failed to receive the status of the lvmscp")
        else:
            replies = scp_status_cmd.replies
            command.info(
                {
                    "z1_arc": replies[-2].body["filename"],
                    "b1_arc": replies[-4].body["filename"],
                    "r1_arc": replies[-6].body["filename"],
                }
            )
            final_data.update(
                {
                    "RIGHT_ARC": {
                        "z1_arc": replies[-2].body["filename"],
                        "b1_arc": replies[-4].body["filename"],
                        "r1_arc": replies[-6].body["filename"],
                    }
                }
            )
        """
        
        if dark:
            #   take the dark image
            command.info("dark image taking . . .")

            
            """
            scp_status_cmd = await command.actor.send_command(
                "lvmscp", f"exposure 1 dark {exptime} {spectro}"
            )
            await scp_status_cmd

            if scp_status_cmd.status.did_fail:
                return command.fail(text="Failed to receive the status of the lvmscp")
            else:
                replies = scp_status_cmd.replies
                command.info(
                    {
                        "z1_dark": replies[-2].body["filename"],
                        "b1_dark": replies[-4].body["filename"],
                        "r1_dark": replies[-6].body["filename"],
                    }
                )

                final_data.update(
                    {
                        "DARK": {
                            "z1_dark": replies[-2].body["filename"],
                            "b1_dark": replies[-4].body["filename"],
                            "r1_dark": replies[-6].body["filename"],
                        }
                    }
                )
                
            """

    # information of the saved files
    command.info(final_data)
    command.finish()


async def check_flat_lamp(command):
    """Check the flat lamp status"""

    flat_lamp_cmd = await (await command.actor.send_command("lvmnps", "status"))
    if flat_lamp_cmd.status.did_fail:
        return False
    else:
        replies = flat_lamp_cmd.replies

        check_lamp = {
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
                command.info(text=f"{key} flat lamp is on!")

        lamp_on.update(check_lamp)
        return lamp_on