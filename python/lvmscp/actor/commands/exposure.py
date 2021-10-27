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

from lvmscp.exceptions import lvmscpError

from . import parser


# logging
log = get_logger("sdss-lvmscp")

# lock for exposure lock
exposure_lock = asyncio.Lock()
log.sh.setLevel(logging.DEBUG)


@parser.command()
@click.argument("COUNT", type=int, default=1, required=False)
@click.argument(
    "FLAVOUR",
    type=click.Choice(["bias", "object", "flat", "dark"]),
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
@click.option(
    "--flush",
    "flush",
    default="no",
    required=False,
    help="Flush before the exposure",
)
async def exposure(
    command, exptime: float, count: int, flavour: str, spectro: str, flush: str
):
    """Exposure command controlling all lower actors"""

    # Check the exposure time input (bias = 0.0)
    log.debug(f"{pretty(datetime.datetime.now())} | Checking exposure time")
    if flavour != "bias" and exptime is None:
        log.error("EXPOSURE-TIME is required unless --flavour=bias.")
        raise click.UsageError("EXPOSURE-TIME is required unless --flavour=bias.")
    elif flavour == "bias":
        exptime = 0.0

    if exptime < 0.0:
        log.error("EXPOSURE-TIME cannot be negative")
        raise click.UsageError("EXPOSURE-TIME cannot be negative")

    # lock for exposure sequence only running for one delegate
    async with exposure_lock:

        log.debug(f"{pretty(datetime.datetime.now())} | Pinging lower actors . . .")
        command.info(text="Pinging . . .")
        err = await check_actor_ping(command, "lvmnps")
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | lvmnps OK!")
            command.info(text="lvmnps OK!")
            pass
        else:
            log.error(err)
            return command.fail(text=err)

        err = await check_actor_ping(command, "archon")
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | archon OK!")
            command.info(text="archon OK!")
            pass
        else:
            log.error(err)
            return command.fail(text=err)

        err = await check_actor_ping(command, "lvmieb")
        if err is True:
            log.info(f"{pretty(datetime.datetime.now())} | lvmieb OK!")
            command.info(text="lvmieb OK!")
            pass
        else:
            log.error(err)
            return command.fail(text=err)

        log.debug("Checking device Power . . .")
        command.info(text="Checking device Power . . .")
        err = await check_device_power(command, spectro)
        if err is True:
            log.info("device power OK!")
            command.info(text="device power OK!")
            pass
        else:
            log.error(err)
            return command.fail(text=err)

        log.debug("Checking Shutter closed . . .")
        command.info(text="Checking Shutter Closed . . .")
        err = await check_shutter_closed(command, spectro)
        if err is True:
            log.info("Shutter Closed!")
            command.info(text="Shutter Closed!")
            pass
        else:
            log.error(err)
            return command.fail(text=err)

        if flavour == "object":
            log.debug("Checking hartmann opened . . .")
            command.info(text="Checking hartmann opened . . .")
            err = await check_hartmann_opened(command, spectro)
            if err is True:
                log.info("Hartmann doors opened!")
                command.info(text="Hartmann doors opened!")
                pass
            else:
                log.error(err)
                return command.fail(text=err)

        log.debug("Checking archon controller initialized . . .")
        command.info(text="Checking archon controller initialized . . .")
        err = await check_archon(command, spectro)
        if err is True:
            log.info("archon initialized!")
            command.info(text="archon initialized!")
            pass
        else:
            log.error(err)
            return command.fail(text=err)

        if flavour == "flat":
            log.debug("Checking flat lamps . . .")
            command.info(text="Checking flat lamps . . .")

            try:
                lamps_on = await check_flat_lamp(command)
                for key, value in lamps_on.items():
                    log.info("{key} arc lamps on!")
                    command.info(text=f"{key} arc lamps on!")
            except Exception as err:
                log.error(err)
                return command.fail(text=err)

        log.info("Starting the exposure.")
        command.info(text="Starting the exposure.")
        # start exposure loop
        for nn in range(count):

            log.info(f"Taking exposure {nn + 1} of {count}.")
            command.info(f"Taking exposure {nn + 1} of {count}.")

            header_json = await extra_header_telemetry(command, spectro)
            print(type(header_json))

            # Flushing before CCD exposure
            if flush == "yes":
                flush_count = 1
                if flush_count > 0:
                    log.info("Flushing . . .")
                    command.info("Flushing . . .")
                    archon_cmd = await (
                        await command.actor.send_command(
                            "archon", f"flush {flush_count}"
                        )
                    )
                    if archon_cmd.status.did_fail:
                        log.error("Failed flushing")
                        return command.fail(text="Failed flushing")

            # Start CCD exposure
            log.debug("Start CCD exposure . . .")
            archon_cmd = await (
                await command.actor.send_command(
                    "archon",
                    f"expose start --controller {spectro} --{flavour} {exptime}",
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
                log.debug(reply[-2].body["text"])
                command.info(text=reply[-2].body["text"])

            if (flavour != "bias" and flavour != "dark") and exptime > 0:
                # Use command to access the actor and command the shutter
                log.info("Opening the shutter")
                command.info("Opening the shutter")

                shutter_cmd = await command.actor.send_command(
                    "lvmieb", f"shutter open {spectro}"
                )
                await shutter_cmd

                if shutter_cmd.status.did_fail:
                    await command.actor.send_command(
                        "lvmieb", f"shutter close {spectro}"
                    )
                    await command.actor.send_command("archon", "expose abort --flush")
                    log.error("Shutter failed to open")
                    return command.fail(text="Shutter failed to open")

                # Report status of the shutter
                replies = shutter_cmd.replies
                shutter_status = replies[-2].body[spectro]["shutter"]
                if shutter_status not in ["opened", "closed"]:
                    log.error(f"Unknown shutter status {shutter_status}.")
                    return command.fail(
                        text=f"Unknown shutter status {shutter_status}."
                    )
                log.info("Shutter is now {shutter_status}.")
                command.info(f"Shutter is now {shutter_status}.")

                if not (
                    await asyncio.create_task(
                        close_shutter_after(command, exptime, spectro)
                    )
                ):
                    await command.actor.send_command("archon", "expose abort --flush")
                    log.error("Failed to close the shutter")
                    return command.fail(text="Failed to close the shutter")
            elif flavour == "dark":
                await asyncio.create_task(stop_exposure_after(command, exptime))

            # Readout pending information
            log.debug("readout . . .")
            command.info(text="readout . . .")
            print(header_json)
            # Finish exposure
            log.debug("archon expose finish --header")
            archon_cmd = await (
                await command.actor.send_command(
                    "archon",
                    "expose finish --header",
                    f"'{header_json}'",
                )
            )

            replies = archon_cmd.replies

            if archon_cmd.status.did_fail:
                command.info(replies[-2].body)
                log.info(replies[-2].body)
                log.error("Failed reading out exposure")
                command.fail(text="Failed reading out exposure")
            else:
                # For monitering the status
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

                command.info(replies[-8].body)
                command.info(replies[-7].body)
                command.info(replies[-6].body)
                command.info(replies[-5].body)
                command.info(replies[-4].body)
                command.info(replies[-3].body)
                command.info(replies[-2].body)

        log.info("Exposure Sequence done!")
        return command.finish(text="Exposure sequence done!")


async def stop_exposure_after(command, delay: float):
    """Waits ``delay`` before closing the shutter."""

    command.info(text="dark exposing . . .")
    await asyncio.sleep(delay)

    return True


async def close_shutter_after(command, delay: float, spectro: str):
    """Waits ``delay`` before closing the shutter."""

    log.info("exposing . . .")
    command.info(text="exposing . . .")
    await asyncio.sleep(delay)

    log.info("Closing the shutter")
    command.info(text="Closing the shutter")
    shutter_cmd = await command.actor.send_command("lvmieb", f"shutter close {spectro}")
    await shutter_cmd

    if shutter_cmd.status.did_fail:
        log.error("Shutter failed to close.")
        command.fail(text="Shutter failed to close.")
        return False

    replies = shutter_cmd.replies
    shutter_status = replies[-2].body[spectro]["shutter"]
    if shutter_status not in ["opened", "closed"]:
        log.error(f"Unknown shutter status {shutter_status!r}.")
        return command.fail(text=f"Unknown shutter status {shutter_status!r}.")

    log.info(f"Shutter is now '{shutter_status}'")
    command.info(text=f"Shutter is now '{shutter_status}'")
    return True


async def check_actor_ping(command, actor_name):

    # Check the actor is running
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
    """Check the open/closed status of the shutter"""
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
    # Check the status (opened / closed) of the hartmann doors
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
    """Check the archon CCD status"""
    # Check that the configuration of archon controller has been loaded.
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


async def check_flat_lamp(command):
    """Check the flat lamp status"""

    flat_lamp_cmd = await (await command.actor.send_command("lvmnps", "status"))
    if flat_lamp_cmd.status.did_fail:
        return "Failed getting status from the network power switch"
    else:
        replies = flat_lamp_cmd.replies

        check_lamp = {
            "625nm LED": replies[-2].body["status"]["DLI-01"]["625 nm LED (M625L4)"][
                "state"
            ],
            "Argon": replies[-2].body["status"]["DLI-03"]["Argon"]["state"],
            "Xenon": replies[-2].body["status"]["DLI-03"]["Xenon"]["state"],
            "HgAr": replies[-2].body["status"]["DLI-03"]["Hg (Ar)"]["state"],
            "LDLS": replies[-2].body["status"]["DLI-03"]["LDLS"]["state"],
            "Krypton": replies[-2].body["status"]["DLI-03"]["Krypton"]["state"],
            "Neon": replies[-2].body["status"]["DLI-03"]["Neon"]["state"],
            "HgNe": replies[-2].body["status"]["DLI-03"]["Hg (Ne)"]["state"],
        }

        sum = 0
        lamp_on = {}

        for key, value in check_lamp.items():
            sum = sum + value
            if value == 1:
                command.info(text=f"{key} flat lamp is on!")
                lamp_on.update(key=value)
            elif sum == 0:
                raise "flat lamp is off..."

        return lamp_on


async def extra_header_telemetry(command, spectro: str):
    """telemetry from the devices and add it on the header"""
    # Build extra header.
    scp_status_cmd = await command.actor.send_command("lvmscp", "status")
    await scp_status_cmd

    if scp_status_cmd.status.did_fail:
        return "Failed to receive the status of the lvmscp"
    else:
        replies = scp_status_cmd.replies
        rhtRH1 = replies[-2].body["IEB"]["HUMIDITY"][spectro]["rhtRH1"]
        rhtRH2 = replies[-2].body["IEB"]["HUMIDITY"][spectro]["rhtRH2"]
        rhtRH3 = replies[-2].body["IEB"]["HUMIDITY"][spectro]["rhtRH3"]
        rhtT1 = replies[-2].body["IEB"]["TEMPERATURE"][spectro]["rhtT1"]
        rhtT2 = replies[-2].body["IEB"]["TEMPERATURE"][spectro]["rhtT2"]
        rhtT3 = replies[-2].body["IEB"]["TEMPERATURE"][spectro]["rhtT3"]
        rtd1 = replies[-2].body["IEB"]["TEMPERATURE"][spectro]["rtd1"]
        rtd2 = replies[-2].body["IEB"]["TEMPERATURE"][spectro]["rtd2"]
        rtd3 = replies[-2].body["IEB"]["TEMPERATURE"][spectro]["rtd3"]
        rtd4 = replies[-2].body["IEB"]["TEMPERATURE"][spectro]["rtd4"]

        if replies[-2].body["LN2VALVE"]["LN2NIR"]:
            ln2_nir = "ON"
        else:
            ln2_nir = "OFF"

        if replies[-2].body["LN2VALVE"]["LN2RED"]:
            ln2_red = "ON"
        else:
            ln2_red = "OFF"

        header_dict = {
            "rhtRH1": (rhtRH1, "IEB rht sensor humidity [%]"),
            "rhtRH2": (rhtRH2, "IEB rht sensor humidity [%]"),
            "rhtRH3": (rhtRH3, "IEB rht sensor humidity [%]"),
            "rhtT1": (rhtT1, "IEB rht sensor Temperature [C]"),
            "rhtT2": (rhtT2, "IEB rht sensor Temperature [C]"),
            "rhtT3": (rhtT3, "IEB rht sensor Temperature [C]"),
            "rtd1": (rtd1, "IEB rtd sensor Temperature [C]"),
            "rtd2": (rtd2, "IEB rtd sensor Temperature [C]"),
            "rtd3": (rtd3, "IEB rtd sensor Temperature [C]"),
            "rtd4": (rtd4, "IEB rtd sensor Temperature [C]"),
            "LN2NIR": (
                ln2_nir,
                "Cryogenic solenoid valve power of NIR camera for LN2",
            ),
            "LN2RED": (
                ln2_red,
                "Cryogenic solenoid valve power of RED camera for LN2",
            ),
        }

        header_json = json.dumps(header_dict, indent=None)
        print(type(header_json))

        return header_json


def pretty(time):
    return f"{bcolors.OKCYAN}{bcolors.BOLD}{time}{bcolors.ENDC}"


def pretty2(time):
    return f"{bcolors.WARNING}{bcolors.BOLD}{time}{bcolors.ENDC}"


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
