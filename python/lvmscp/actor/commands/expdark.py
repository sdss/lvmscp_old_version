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
async def expdark(
    command,
    supervisors: dict[str, Supervisor],
    exptime: float,
    count: int,
    spectro: str,
):
    """command for dark after object sequence"""

    final_data = {}
    # calculate the integrated time
    for spectro in supervisors:
        if supervisors[spectro].ready:
            if supervisors[spectro].readoutmode == "800":
                integ_time = (exptime + 47) * 2 * count
            elif supervisors[spectro].readoutmode == "400":
                integ_time = (exptime + 20) * 2 * count

    command.info(f"Total exposure time will be = {integ_time} sec")

    for spectro in supervisors:
        if supervisors[spectro].ready:
            # Loop for counts
            # start exposure loop
            for nn in range(count):

                #   Take the arc image
                filename = await supervisors[spectro].exposure(
                    command, exptime, 1, "object"
                )

                final_data.update(
                    {
                        "OBJECT": {
                            "z1_object": filename[0],
                            "b1_object": filename[1],
                            "r1_object": filename[2],
                        }
                    }
                )

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
