import asyncio
import logging

import click
from clu.command import Command

from sdsstools import get_logger

from . import parser


# logging
log = get_logger("sdss-lvmscp")

log.sh.setLevel(logging.DEBUG)


@parser.command()
@click.argument(
    "spectro",
    type=click.Choice(["sp1", "sp2", "sp3"]),
    default="sp1",
    required=False,
)
async def status(command: Command, spectro: str):
    """Receive all of the telemetry related to the spectrograph"""
    # check the power of the network power switch

    nps_status_cmd = await command.actor.send_command("lvmnps", "status all")
    await nps_status_cmd

    if nps_status_cmd.status.did_fail:
        command.info(text="Failed to receive the power status from wago relays")
    else:
        nps_replies = nps_status_cmd.replies

    # check the power of the shutter & hartmann doors

    shutter_power_status = "ERROR"
    hartmann_left_power_status = "ERROR"
    hartmann_right_power_status = "ERROR"

    wago_power_status_cmd = await command.actor.send_command(
        "lvmieb", f"wago getpower {spectro}"
    )
    await wago_power_status_cmd

    if wago_power_status_cmd.status.did_fail:
        command.info(text="Failed to receive the power status from wago relays")
    else:
        replies = wago_power_status_cmd.replies
        shutter_power_status = replies[-1].body["shutter_power"]
        hartmann_left_power_status = replies[-1].body["hartmann_left_power"]
        hartmann_right_power_status = replies[-1].body["hartmann_right_power"]

    # Check the status (opened / closed) of the shutter
    shutter_status = "ERROR"
    shutter_status_cmd = await command.actor.send_command(
        "lvmieb", f"shutter status {spectro}"
    )
    await shutter_status_cmd

    if shutter_status_cmd.status.did_fail:
        command.info(text="Failed to receive the status of the shutter status")
    else:
        replies = shutter_status_cmd.replies
        shutter_status = replies[-1].body["shutter"]

    # Check the status (opened / closed) of the hartmann doors
    hartmann_left_status = "ERROR"
    hartmann_right_status = "ERROR"

    hartmann_status_cmd = await command.actor.send_command(
        "lvmieb", f"hartmann status {spectro}"
    )
    await hartmann_status_cmd

    if hartmann_status_cmd.status.did_fail:
        command.info(text="Failed to receive the status of the hartmann status")
    else:
        replies = hartmann_status_cmd.replies
        hartmann_left_status = replies[-1].body["hartmann_left"]
        hartmann_right_status = replies[-1].body["hartmann_right"]

    # Check the status of the wago module (wago status)

    rhtRH1 = "ERROR"
    rhtT1 = "ERROR"
    rhtRH2 = "ERROR"
    rhtT2 = "ERROR"
    rhtRH3 = "ERROR"
    rhtT3 = "ERROR"
    rtd1 = "ERROR"
    rtd2 = "ERROR"
    rtd3 = "ERROR"
    rtd4 = "ERROR"

    wago_telemetry_status_cmd = await command.actor.send_command(
        "lvmieb", f"wago status {spectro}"
    )
    await wago_telemetry_status_cmd

    if wago_telemetry_status_cmd.status.did_fail:
        command.info(text="Failed to receive the telemetry status from wago sensors")
    else:
        replies = wago_telemetry_status_cmd.replies

        rhtRH1 = replies[-1].body["rhtRH1"]
        rhtT1 = replies[-1].body["rhtT1"]
        rhtRH2 = replies[-1].body["rhtRH2"]
        rhtT2 = replies[-1].body["rhtT2"]
        rhtRH3 = replies[-1].body["rhtRH3"]
        rhtT3 = replies[-1].body["rhtT3"]
        rtd1 = replies[-1].body["rtd1"]
        rtd2 = replies[-1].body["rtd2"]
        rtd3 = replies[-1].body["rtd3"]
        rtd4 = replies[-1].body["rtd4"]

    # Check the status of the transducer
    r1_pressure = "ERROR"
    b1_pressure = "ERROR"
    z1_pressure = "ERROR"
    r1_temperature = "ERROR"
    b1_temperature = "ERROR"
    z1_temperature = "ERROR"

    transducer_status_cmd = await asyncio.wait_for(
        command.actor.send_command("lvmieb", f"transducer status {spectro}"), 1
    )
    await transducer_status_cmd

    if transducer_status_cmd.status.did_fail:
        command.info(text="Failed to receive the telemetry status from transducer")
    else:
        replies = transducer_status_cmd.replies

        r1_pressure = replies[-1].body["r1_pressure"]
        b1_pressure = replies[-1].body["b1_pressure"]
        z1_pressure = replies[-1].body["z1_pressure"]
        r1_temperature = replies[-1].body["r1_temperature"]
        b1_temperature = replies[-1].body["b1_temperature"]
        z1_temperature = replies[-1].body["z1_temperature"]

    log.info("status logged successfully!")
    command.info(
        IEB_POWER={
            "shutter_power_status": shutter_power_status,
            "hartmann_left_power_status": hartmann_left_power_status,
            "hartmann_right_power_status": hartmann_right_power_status,
        },
        ACTION={
            "shutter_status": shutter_status,
            "hartmann_left_status": hartmann_left_status,
            "hartmann_right_status": hartmann_right_status,
        },
        IEB_HUMIDITY={"rhtRH1": rhtRH1, "rhtRH2": rhtRH2, "rhtRH3": rhtRH3},
        IEB_TEMPERATURE={
            "rhtT1": rhtT1,
            "rhtT2": rhtT2,
            "rhtT3": rhtT3,
            "rtd1": rtd1,
            "rtd2": rtd2,
            "rtd3": rtd3,
            "rtd4": rtd4,
        },
        TRANSDUCER_TEMP={
            "r1": r1_temperature,
            "b1": b1_temperature,
            "z1": z1_temperature,
        },
        TRANSDUCER_PRES={"r1": r1_pressure, "b1": b1_pressure, "z1": z1_pressure},
        NETWORK_POWER_SWITCHES=nps_replies[-2].body,
    )
    return command.finish(text="done")
