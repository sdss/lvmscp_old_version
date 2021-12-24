#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong YANG (mingyeong@khu.ac.kr)
# @Date: 2021-03-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import datetime
import json
import logging

import click

from sdsstools import get_logger

from lvmscp.actor.supervisor import Supervisor
from lvmscp.exceptions import lvmscpError

from . import parser


# from clu.parsers.click import command_parser


# logging
log = get_logger("sdss-lvmscp")

# lock for exposure lock
exposure_lock = asyncio.Lock()
log.sh.setLevel(logging.DEBUG)


@parser.command()
@click.argument("COUNT", type=int, default=1, required=False)
@click.argument(
    "FLAVOUR",
    type=click.Choice(["bias", "object", "arc", "dark"]),
    default="object",
    required=False,
)
@click.argument("EXPTIME", type=float, required=False)
@click.argument(
    "spectro",
    type=click.Choice(["sp1", "sp2", "sp3"]),
    default="sp1",
    required=False,
)
@click.argument("BINNING", type=int, default=1, required=False)
@click.argument("HEADER", type=str, default="{}", required=False)
@click.option(
    "--flush",
    "flush",
    default="no",
    required=False,
    help="Flush before the exposure",
)
async def exposure(
    command,
    supervisors: dict[str, Supervisor],
    exptime: float,
    count: int,
    flavour: str,
    spectro: str,
    binning: int,
    flush: str,
    header: str,
):
    """This is the exposure command for running the exposure sequnce.

    Args:
        command ([type]): Command class from clu.actor.Commands
        supervisors (dict[str, Supervisor]): Supervisor class from lvmscp.supervisor.py
        exptime (float): exposure time
        count (int): count of frames
        flavour (str): bias/dark/arc/object type of image
        spectro (str): sp1/sp2/sp3 the spectrograph to take exposure.
        binning (int): binning of the CCD camera
        flush (str): flushing parameter, not required
        header (str): header metadata. The example structure is like such: '\'{"test": 1}\''

    Raises:
        click.UsageError: UsageError for the click class

    Returns:
        [type]: command.finish(filename={array of the files})
    """
    data_directory = []

    # Check the exposure time input (bias = 0.0)
    log.debug(f"{pretty(datetime.datetime.now())} | Checking exposure time")
    if flavour != "bias" and exptime is None:
        log.error(
            f"{pretty(datetime.datetime.now())} | EXPOSURE-TIME is required unless --flavour=bias."
        )
        raise click.UsageError("EXPOSURE-TIME is required unless --flavour=bias.")
    elif flavour == "bias":
        exptime = 0.0

    if exptime < 0.0:
        log.error(
            f"{pretty(datetime.datetime.now())} | EXPOSURE-TIME cannot be negative"
        )
        raise click.UsageError("EXPOSURE-TIME cannot be negative")

    # lock for exposure sequence only running for one delegate
    async with exposure_lock:

        # pinging lower actors
        log.debug(f"{pretty(datetime.datetime.now())} | Pinging lower actors . . .")
        command.info(text="Pinging . . .")
        err = await check_actor_ping(command, "lvmnps")
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | lvmnps OK!")
            command.info(text="lvmnps OK!")
            pass
        else:
            log.error(f"{pretty(datetime.datetime.now())} | {err}")
            return command.fail(text=err)

        err = await check_actor_ping(command, "archon")
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | archon OK!")
            command.info(text="archon OK!")
            pass
        else:
            log.error(f"{pretty(datetime.datetime.now())} | {err}")
            return command.fail(text=err)

        err = await check_actor_ping(command, "lvmieb")
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | lvmieb OK!")
            command.info(text="lvmieb OK!")
            pass
        else:
            log.error(f"{pretty(datetime.datetime.now())} | {err}")
            return command.fail(text=err)

        # check the power of shutter and hartmann doors
        log.debug(f"{pretty(datetime.datetime.now())} | Checking device Power . . .")
        command.info(text="Checking device Power . . .")
        err = await check_device_power(command, spectro)
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | device power OK!")
            command.info(text="device power OK!")
            pass
        else:
            log.error(f"{pretty(datetime.datetime.now())} | {err}")
            return command.fail(text=err)

        # Checking the shutter is already closed
        log.debug(f"{pretty(datetime.datetime.now())} | Checking Shutter closed . . .")
        command.info(text="Checking Shutter Closed . . .")
        err = await check_shutter_closed(command, spectro)
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | Shutter Closed!")
            command.info(text="Shutter Closed!")
            pass
        else:
            log.error(f"{pretty(datetime.datetime.now())} | {err}")
            return command.fail(text=err)

        # when the flavour is object
        if flavour == "object":
            # Check the hartmann door is all opened for the science exposure
            log.debug(
                f"{pretty(datetime.datetime.now())} | Checking hartmann opened . . ."
            )
            command.info(text="Checking hartmann opened . . .")
            err = await check_hartmann_opened(command, spectro)
            if err is True:
                log.info(f"{pretty(datetime.datetime.now())} | Hartmann doors opened!")
                command.info(text="Hartmann doors opened!")
                pass
            else:
                log.error(f"{pretty(datetime.datetime.now())} | {err}")
                return command.fail(text=err)

        # Check the archon controller is initialized and on the status of IDLE
        log.debug(
            f"{pretty(datetime.datetime.now())} | Checking archon controller initialized . . ."
        )
        command.info(text="Checking archon controller initialized . . .")
        err = await check_archon(command, spectro)
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | archon initialized!")
            command.info(text="archon initialized!")
            pass
        else:
            log.error(f"{pretty(datetime.datetime.now())} | {err}")
            return command.fail(text=err)

        # Check the status of lamps for arc exposure
        check_lamp = None
        if flavour == "arc":
            log.debug(f"{pretty(datetime.datetime.now())} | Checking arc lamps . . .")
            command.info(text="Checking arc lamps . . .")

            try:
                check_lamp = await check_arc_lamp(command)
            except Exception as err:
                log.error(f"{pretty(datetime.datetime.now())} | {err}")
                return command.fail(text=err)

            if check_lamp:
                sum = 0
                lamp_on = {}
                for key, value in check_lamp.items():
                    sum = sum + value
                    if value == 1:
                        log.info(
                            f"{pretty(datetime.datetime.now())} | {key} arc lamps on!"
                        )
                        command.info(text=f"{key} arc lamp is on!")
                        lamp_on.update(key=value)
                log.debug(f"{pretty(datetime.datetime.now())} | sum is {sum}")
                if sum == 0:
                    return command.fail(text="arc lamps are all off . . .")
            elif not check_lamp:
                return command.fail(text="Power Switch status is not Reading . . .")

        # starting the exposure
        log.info(f"{pretty(datetime.datetime.now())} | Starting the exposure.")
        command.info(text="Starting the exposure.")
        # start exposure loop
        for nn in range(count):

            log.info(
                f"{pretty(datetime.datetime.now())} | Taking exposure {nn + 1} of {count}."
            )
            command.info(text=f"Taking exposure {nn + 1} of {count}.")
            # receive the telemetry data to add on the FIT header
            header_json = await extra_header_telemetry(
                command, spectro, check_lamp, supervisors, header
            )

            # Flushing before CCD exposure
            if flush == "yes":
                flush_count = 1
                if flush_count > 0:
                    log.info(f"{pretty(datetime.datetime.now())} | Flushing . . .")
                    command.info(text="Flushing . . .")
                    archon_cmd = await (
                        await command.actor.send_command(
                            "archon", f"flush {flush_count}"
                        )
                    )
                    if archon_cmd.status.did_fail:
                        log.error(
                            f"{pretty(datetime.datetime.now())} | Failed flushing"
                        )
                        return command.fail(text="Failed flushing")

            # Start CCD exposure
            log.info(f"{pretty(datetime.datetime.now())} | Start CCD exposure . . .")

            # archon has to send flavour flat for arc lamps
            if flavour == "arc":
                flavour = "flat"

            # send exposure command to archon
            archon_cmd = await (
                await command.actor.send_command(
                    "archon",
                    f"expose start --controller {spectro} --{flavour} --binning {binning} {exptime}",  # noqa E501
                )
            )
            if archon_cmd.status.did_fail:
                await command.actor.send_command("archon", "expose abort --flush")
                log.error(
                    f"{pretty2(datetime.datetime.now())} | Failed starting exposure. Trying to abort and exiting."  # noqa E501
                )
                return command.fail(
                    text="Failed starting exposure. Trying to abort and exiting."
                )
            else:
                reply = archon_cmd.replies
                log.debug(
                    f"{pretty(datetime.datetime.now())} | {reply[-2].body['text']}"
                )
                command.info(text=reply[-2].body["text"])

            # opening the shutter for arc and object type frame
            if (flavour != "bias" and flavour != "dark") and exptime > 0:
                # Use command to access the actor and command the shutter
                log.info(f"{pretty(datetime.datetime.now())} | Opening the shutter")
                command.info(text="Opening the shutter")

                shutter_cmd = await command.actor.send_command(
                    "lvmieb", f"shutter open {spectro}"
                )
                await shutter_cmd

                if shutter_cmd.status.did_fail:
                    await command.actor.send_command(
                        "lvmieb", f"shutter close {spectro}"
                    )
                    await command.actor.send_command("archon", "expose abort --flush")
                    log.error(
                        f"{pretty(datetime.datetime.now())} | Shutter failed to open"
                    )
                    return command.fail(text="Shutter failed to open")

                # Report status of the shutter
                replies = shutter_cmd.replies
                shutter_status = replies[-2].body[spectro]["shutter"]
                if shutter_status not in ["opened", "closed"]:
                    log.error(
                        f"{pretty(datetime.datetime.now())} | Unknown shutter status {shutter_status}."  # noqa E501
                    )
                    return command.fail(
                        text=f"Unknown shutter status {shutter_status}."
                    )
                log.info(
                    f"{pretty(datetime.datetime.now())} | Shutter is now {shutter_status}."
                )
                command.info(text=f"Shutter is now {shutter_status}.")

                if not (
                    await asyncio.create_task(
                        close_shutter_after(command, exptime, spectro)
                    )
                ):
                    await command.actor.send_command("archon", "expose abort --flush")
                    log.error(
                        f"{pretty(datetime.datetime.now())} | Failed to close the shutter"
                    )
                    return command.fail(text="Failed to close the shutter")
            # dark frame doesn't have to open the shutter
            elif flavour == "dark":
                await asyncio.create_task(wait_exposure(command, exptime))

            # Finish exposure
            log.debug(
                f"{pretty(datetime.datetime.now())} | archon expose finish --header"
            )
            log.debug(f"{pretty(datetime.datetime.now())} | {header_json}")

            # Readout pending information
            log.debug(f"{pretty(datetime.datetime.now())} | readout . . .")
            command.info(text="readout . . .")

            # send the exposure finish command
            archon_cmd = await (
                await command.actor.send_command(
                    "archon",
                    "expose finish --header",
                    f"'{header_json}'",
                )
            )

            replies = archon_cmd.replies

            if archon_cmd.status.did_fail:
                # command.info(replies[-2].body)
                log.info(f"{pretty(datetime.datetime.now())} | {replies[-2].body}")
                log.error(
                    f"{pretty(datetime.datetime.now())} | Failed reading out exposure"
                )
                return command.fail(text="Failed reading out exposure")

            else:
                # wait until the status of the archon changes into IDLE
                while True:
                    readout_cmd = await command.actor.send_command("archon", "status")
                    await readout_cmd
                    readout_replies = readout_cmd.replies
                    archon_readout = readout_replies[-2].body["status"]["status_names"][
                        0
                    ]
                    if archon_readout == "READING":
                        continue
                    else:
                        command.info(text="readout finished!")
                        break

                command.info(reply=replies[-8].body)
                command.info(reply=replies[-7].body)
                command.info(reply=replies[-6].body)
                command.info(reply=replies[-5].body)
                command.info(reply=replies[-4].body)
                command.info(reply=replies[-3].body)
                command.info(reply=replies[-2].body)

                data_directory.append(replies[-2].body["filename"])
                data_directory.append(replies[-4].body["filename"])
                data_directory.append(replies[-6].body["filename"])

        log.info(f"{pretty(datetime.datetime.now())} | Exposure Sequence done!")
        command.info(text="Exposure Sequence done!")
        return command.finish(filename=data_directory)


async def wait_exposure(command, delay: float):
    """Waits ``delay`` before closing the shutter for dark exposure

    Args:
        command ([type]): [description]
        delay (float): same with exptime

    Returns:
        True
    """

    command.info(text="dark exposing . . .")
    await asyncio.sleep(delay)

    return True


async def close_shutter_after(command, delay: float, spectro: str):
    """Waits ``delay`` before closing the shutter.

    Args:
        command ([type]): [description]
        delay (float): [description]
        spectro (str): [description]

    Returns:
        [type]: [description]
    """

    log.info(f"{pretty(datetime.datetime.now())} | exposing . . .")
    command.info(text="exposing . . .")
    await asyncio.sleep(delay)

    log.info(f"{pretty(datetime.datetime.now())} | Closing the shutter")
    command.info(text="Closing the shutter")
    shutter_cmd = await command.actor.send_command("lvmieb", f"shutter close {spectro}")
    await shutter_cmd

    if shutter_cmd.status.did_fail:
        log.error(f"{pretty(datetime.datetime.now())} | Shutter failed to close.")
        return command.fail(text="Shutter failed to close.")

    replies = shutter_cmd.replies
    shutter_status = replies[-2].body[spectro]["shutter"]
    if shutter_status not in ["opened", "closed"]:
        log.error(
            f"{pretty(datetime.datetime.now())} | Unknown shutter status {shutter_status!r}."
        )
        return command.fail(text=f"Unknown shutter status {shutter_status!r}.")

    log.info(f"{pretty(datetime.datetime.now())} | Shutter is now {shutter_status}")
    command.info(text=f"Shutter is now {shutter_status}")
    return True


async def check_actor_ping(command, actor_name: str):
    """Send the ping command to lower actors (lvmieb, archon, lvmnps) and check if they are running

    Args:
        command ([type]): clu.actor.Command class
        actor_name (str): name of the actor to send the ping command

    Returns:
        err string
        or
        True (boolian)
    """
    try:
        status_cmd = await command.actor.send_command(actor_name, "ping")
        await status_cmd
    except lvmscpError as err:
        return str(err)

    if status_cmd.status.did_fail:
        return status_cmd.status
    else:
        return True


async def check_device_power(command, spectro: str):
    """Check the power of devices controlled by wago power module.
    Especially the power of shutter and the hartmann door.

    Args:
        command ([type]): clu.actor.Command
        spectro (str): which spectrograph to check sp1/sp2/sp3

    Returns:
        err string
        or
        True
    """

    # check the power of the shutter & hartmann doors
    wago_power_status_cmd = await command.actor.send_command(
        "lvmieb", f"wago getpower {spectro}"
    )
    await wago_power_status_cmd

    if wago_power_status_cmd.status.did_fail:
        return "Failed to receive the power status from wago relays"
    else:
        replies = wago_power_status_cmd.replies
        shutter_power_status = replies[-2].body[spectro]["shutter_power"]
        hartmann_left_power_status = replies[-2].body[spectro]["hartmann_left_power"]
        hartmann_right_power_status = replies[-2].body[spectro]["hartmann_right_power"]

        if shutter_power_status == "OFF":
            return "Cannot start exposure : Exposure shutter power off"
        elif hartmann_left_power_status == "OFF":
            return "Cannot start exposure : Left hartmann door power off"
        elif hartmann_right_power_status == "OFF":
            return "Cannot start exposure : Right hartmann door power off"
        else:
            return True


async def check_shutter_closed(command, spectro: str):
    """Check the open/closed status of the shutter

    Args:
        command ([type]): [description]
        spectro (str): sp1/sp2/sp3

    Returns:
        [type]: [description]
    """
    shutter_status_cmd = await command.actor.send_command(
        "lvmieb", f"shutter status {spectro}"
    )
    await shutter_status_cmd

    if shutter_status_cmd.status.did_fail:
        return "Failed to receive the status of the shutter status"
    else:
        replies = shutter_status_cmd.replies
        shutter_status_before = replies[-2].body[spectro]["shutter"]

        if shutter_status_before != "closed":
            return "Shutter is already opened. The command will fail"
        else:
            return True


async def check_hartmann_opened(command, spectro: str):
    """Check the status (opened / closed) of the hartmann doors

    Args:
        command ([type]): [description]
        spectro (str): [description]

    Returns:
        [type]: [description]
    """
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

        if not (hartmann_left_status == "opened" and hartmann_right_status == "opened"):
            return "Hartmann doors are not opened for the science exposure"
        else:
            return True


async def check_archon(command, spectro: str):
    """Check that the configuration of archon controller has been loaded.

    Args:
        command ([type]): [description]
        spectro (str): [description]

    Returns:
        [type]: [description]
    """
    archon_cmd = await (await command.actor.send_command("archon", "status"))
    if archon_cmd.status.did_fail:
        return "Failed getting status from the controller"
    else:
        replies = archon_cmd.replies
        check_idle = replies[-2].body["status"]["status_names"][0]
        if check_idle != "IDLE":
            return "archon is not initialized"
        else:
            return True


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

        return check_lamp


async def extra_header_telemetry(
    command, spectro: str, check_lamp, supervisors, header: str
):
    """telemetry from the devices and add it on the header

    Args:
        command ([type]): [description]
        spectro (str): [description]
        check_lamp ([type]): [description]
        supervisors ([type]): [description]
        header (str): [description]

    Returns:
        [type]: [description]
    """

    if supervisors[spectro].ready:
        await supervisors[spectro].UpdateStatus(command)

    left = -1
    if supervisors[spectro].hartmann_left_status == "opened":
        left = 0
    elif supervisors[spectro].hartmann_left_status == "closed":
        left = 1

    right = -1
    if supervisors[spectro].hartmann_right_status == "opened":
        right = 0
    elif supervisors[spectro].hartmann_right_status == "closed":
        right = 1

    header_dict = {
        "rhtRH1": (supervisors[spectro].rhtRH1, "IEB rht sensor humidity [%]"),
        "rhtRH2": (supervisors[spectro].rhtRH2, "IEB rht sensor humidity [%]"),
        "rhtRH3": (supervisors[spectro].rhtRH3, "IEB rht sensor humidity [%]"),
        "rhtT1": (supervisors[spectro].rhtT1, "IEB rht sensor Temperature [C]"),
        "rhtT2": (supervisors[spectro].rhtT2, "IEB rht sensor Temperature [C]"),
        "rhtT3": (supervisors[spectro].rhtT3, "IEB rht sensor Temperature [C]"),
        "rtd1": (supervisors[spectro].rtd1, "IEB rtd sensor Temperature [C]"),
        "rtd2": (supervisors[spectro].rtd2, "IEB rtd sensor Temperature [C]"),
        "rtd3": (supervisors[spectro].rtd3, "IEB rtd sensor Temperature [C]"),
        "rtd4": (supervisors[spectro].rtd4, "IEB rtd sensor Temperature [C]"),
        "LN2NIR": (
            supervisors[spectro].ln2nir,
            "Cryogenic solenoid valve power of NIR camera for LN2",
        ),
        "LN2RED": (
            supervisors[spectro].ln2red,
            "Cryogenic solenoid valve power of RED camera for LN2",
        ),
        "HARTMANN": (f"{left} {right}", "Left/right. 0=open 1=closed"),
        "RPRESS": (
            supervisors[spectro].r1_pressure,
            "Pressure from the transducer of r1 cryostat",
        ),
        "BPRESS": (
            supervisors[spectro].b1_pressure,
            "Pressure from the transducer of b1 cryostat",
        ),
        "ZPRESS": (
            supervisors[spectro].z1_pressure,
            "Pressure from the transducer of z1 cryostat",
        ),
        supervisors[spectro].testccd: {
            "DEPTHA": supervisors[spectro].gage_A,
            "DEPTHB": supervisors[spectro].gage_B,
            "DEPTHC": supervisors[spectro].gage_C,
        },
    }
    if check_lamp:
        for key, value in check_lamp.items():
            if value:
                check_lamp[key] = "ON"
            else:
                check_lamp[key] = "OFF"

        log.debug(f"{pretty(datetime.datetime.now())} | check_lamp: {check_lamp}")
        header_dict.update(check_lamp)
    log.debug(f"{pretty(datetime.datetime.now())} | header_dict: {header_dict}")

    # adding header to here 20211222 CK

    extra_header = json.loads(header)
    if header:
        header_dict.update(extra_header)

    header_json = json.dumps(header_dict, indent=None)

    return header_json


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
