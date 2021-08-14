from clu.command import Command

from . import parser


@parser.command()
async def status(command: Command):
    """Receive all of the telemetry related to the spectrograph"""
    # check the power of the network power switch
    nps_status_cmd = await command.actor.send_command("lvmnps", "status all")
    await nps_status_cmd

    if nps_status_cmd.status.did_fail:
        return command.fail(text="Failed to receive the power status from wago relays")

    nps_replies = nps_status_cmd.replies

    # check the power of the shutter & hartmann doors
    wago_power_status_cmd = await command.actor.send_command("lvmieb", "wago getpower")
    await wago_power_status_cmd

    if wago_power_status_cmd.status.did_fail:
        return command.fail(text="Failed to receive the power status from wago relays")

    replies = wago_power_status_cmd.replies

    shutter_power_status = replies[-1].body["shutter_power"]
    hartmann_left_power_status = replies[-1].body["hartmann_left_power"]
    hartmann_right_power_status = replies[-1].body["hartmann_right_power"]

    # Check the status (opened / closed) of the shutter
    shutter_status_cmd = await command.actor.send_command("lvmieb", "shutter status")
    await shutter_status_cmd

    if shutter_status_cmd.status.did_fail:
        return command.fail(text="Failed to receive the status of the shutter status")

    replies = shutter_status_cmd.replies
    shutter_status = replies[-1].body["shutter"]

    # Check the status (opened / closed) of the hartmann doors
    hartmann_status_cmd = await command.actor.send_command("lvmieb", "hartmann status")
    await hartmann_status_cmd

    if hartmann_status_cmd.status.did_fail:
        return command.fail(text="Failed to receive the status of the hartmann status")

    replies = hartmann_status_cmd.replies
    hartmann_left_status = replies[-1].body["hartmann_left"]
    hartmann_right_status = replies[-1].body["hartmann_right"]

    # Check the status of the wago module (wago status)
    wago_telemetry_status_cmd = await command.actor.send_command(
        "lvmieb", "wago status"
    )
    await wago_telemetry_status_cmd

    if wago_telemetry_status_cmd.status.did_fail:
        return command.fail(
            text="Failed to receive the telemetry status from wago sensors"
        )

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
    transducer_status_cmd = await command.actor.send_command(
        "lvmieb", "transducer status"
    )
    await transducer_status_cmd

    if transducer_status_cmd.status.did_fail:
        return command.fail(
            text="Failed to receive the telemetry status from wago sensors"
        )

    replies = transducer_status_cmd.replies

    r1_pressure = replies[-1].body["r1_pressure"]
    b1_pressure = replies[-1].body["b1_pressure"]
    z1_pressure = replies[-1].body["z1_pressure"]
    r1_temperature = replies[-1].body["r1_temperature"]
    b1_temperature = replies[-1].body["b1_temperature"]
    z1_temperature = replies[-1].body["z1_temperature"]

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
