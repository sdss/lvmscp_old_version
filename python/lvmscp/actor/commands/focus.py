import logging

import click

from sdsstools import get_logger

from lvmscp.actor.supervisor import Supervisor

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
    # calculate the integrated time
    for spectro in supervisors:
        if supervisors[spectro].ready:
            if supervisors[spectro].readoutmode == "800":
                if dark:
                    integ_time = (exptime + 47) * 3 * count
                else:
                    integ_time = (exptime + 47) * 2 * count
            elif supervisors[spectro].readoutmode == "400":
                if dark:
                    integ_time = (exptime + 20) * 3 * count  # 19.4 second
                else:
                    integ_time = (exptime + 20) * 2 * count

    command.info(f"Total exposure time will be = {integ_time} sec")

    # Check if lamp is on
    log.debug("Checking arc lamps . . .")
    command.info(text="Checking arc lamps . . .")

    for spectro in supervisors:
        if supervisors[spectro].ready:
            lamps_on = await supervisors[spectro].check_arc_lamp(command)

            if lamps_on is False:
                return command.fail(text="The arc lamps are all off . . .")

            final_data.update(lamps_on)

            # Loop for counts
            # start exposure loop
            for nn in range(count):

                #   set the hartmann door - left
                command.info("hartmann left setting . . .")
                await supervisors[spectro].SetHartmann(command, "left")

                #   Take the arc image
                filename = await supervisors[spectro].exposure(
                    command, exptime, 1, "arc"
                )

                final_data.update(
                    {
                        "LEFT_ARC": {
                            "z1_arc": filename[0],
                            "b1_arc": filename[1],
                            "r1_arc": filename[2],
                        }
                    }
                )

                #   set the hartmann door - right
                command.info("hartmann right setting . . .")
                await supervisors[spectro].SetHartmann(command, "right")

                #   Take the arc image
                command.info("arc image taking . . .")
                filename = await supervisors[spectro].exposure(
                    command, exptime, 1, "arc"
                )

                final_data.update(
                    {
                        "RIGHT_ARC": {
                            "z1_arc": filename[0],
                            "b1_arc": filename[1],
                            "r1_arc": filename[2],
                        }
                    }
                )

                if dark:
                    #   take the dark image
                    command.info("dark image taking . . .")

                    filename = await supervisors[spectro].exposure(
                        command, exptime, 1, "dark"
                    )

                    final_data.update(
                        {
                            "DARK": {
                                "z1_dark": filename[0],
                                "b1_dark": filename[1],
                                "r1_dark": filename[2],
                            }
                        }
                    )

    # information of the saved files
    print(final_data)
    command.info(data=final_data)
    command.finish()
