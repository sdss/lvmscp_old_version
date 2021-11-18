import asyncio
import logging

from clu.command import Command

from sdsstools import get_logger

from lvmscp.actor.supervisor import Supervisor

from . import parser


# logging
log = get_logger("sdss-lvmscp")

log.sh.setLevel(logging.DEBUG)

spectro_list = ["sp1", "sp2", "sp3"]


@parser.command()
async def status(command: Command, supervisors: dict[str, Supervisor]):
    """Receive all of the telemetry related to the spectrograph"""
    # check the power of the network power switch

    nps_status_cmd = await command.actor.send_command("lvmnps", "status")
    await nps_status_cmd

    if nps_status_cmd.status.did_fail:
        command.info(text="Failed to receive the power status from wago relays")
    else:
        replies = nps_status_cmd.replies

    ln2nir = convert(replies[-2].body["status"]["DLI-02"]["LN2 NIR Valve"]["state"])
    ln2red = convert(replies[-2].body["status"]["DLI-02"]["LN2 Red Valve"]["state"])

    archon_power_nps = convert(
        replies[-2].body["status"]["DLI-02"]["LVM-Archon-02"]["state"]
    )

    argon = convert(replies[-2].body["status"]["DLI-03"]["Argon"]["state"])
    xenon = convert(replies[-2].body["status"]["DLI-03"]["Xenon"]["state"])
    hgar = convert(replies[-2].body["status"]["DLI-03"]["Hg (Ar)"]["state"])
    ldls = convert(replies[-2].body["status"]["DLI-03"]["LDLS"]["state"])
    krypton = convert(replies[-2].body["status"]["DLI-03"]["Krypton"]["state"])
    neon = convert(replies[-2].body["status"]["DLI-03"]["Neon"]["state"])
    hgne = convert(replies[-2].body["status"]["DLI-03"]["Hg (Ne)"]["state"])

    ieb06 = convert(replies[-2].body["status"]["DLI-02"]["IEB06"]["state"])

    rpi = convert(replies[-2].body["status"]["DLI-02"]["RPi"]["state"])
    pres_transducer = convert(
        replies[-2].body["status"]["DLI-02"]["Pressure transducers"]["state"]
    )

    # check the status of archon controller

    archon_status_cmd = await command.actor.send_command("archon", "status")
    await archon_status_cmd

    if archon_status_cmd.status.did_fail:
        command.info(text="Failed to receive the status from archon")
    else:
        replies = archon_status_cmd.replies
        archon_status = replies[-2].body["status"]["status_names"]
        r1ccd_temp = replies[-2].body["status"]["mod2/tempa"]
        b1ccd_temp = replies[-2].body["status"]["mod12/tempb"]
        z1ccd_temp = replies[-2].body["status"]["mod12/tempa"]
        r1heater = replies[-2].body["status"]["mod2/heateraoutput"]
        b1heater = replies[-2].body["status"]["mod12/heateraoutput"]
        z1heater = replies[-2].body["status"]["mod12/heaterboutput"]

    # adding the status of other spectrographs 20210908
    # work from here to add the status of multiple spectrographes
    for spectro in supervisors:
        if supervisors[spectro].ready:
            wago_power_status_cmd = await command.actor.send_command(
                "lvmieb", f"wago getpower {spectro}"
            )
            await wago_power_status_cmd

            if wago_power_status_cmd.status.did_fail:
                command.info(text="Failed to receive the power status from wago relays")
            else:
                replies = wago_power_status_cmd.replies
                supervisors[spectro].shutter_power_status = replies[-2].body[spectro][
                    "shutter_power"
                ]
                supervisors[spectro].hartmann_left_power_status = replies[-2].body[
                    spectro
                ]["hartmann_left_power"]
                supervisors[spectro].hartmann_right_power_status = replies[-2].body[
                    spectro
                ]["hartmann_right_power"]

            # Check the status (opened / closed) of the shutter
            shutter_status_cmd = await command.actor.send_command(
                "lvmieb", f"shutter status {spectro}"
            )
            await shutter_status_cmd

            if shutter_status_cmd.status.did_fail:
                command.info(text="Failed to receive the status of the shutter status")
            else:
                replies = shutter_status_cmd.replies
                supervisors[spectro].shutter_status = replies[-2].body[spectro][
                    "shutter"
                ]

            # Check the status (opened / closed) of the hartmann doors

            hartmann_status_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann status {spectro}"
            )
            await hartmann_status_cmd

            if hartmann_status_cmd.status.did_fail:
                command.info(text="Failed to receive the status of the hartmann status")
            else:
                replies = hartmann_status_cmd.replies
                supervisors[spectro].hartmann_left_status = replies[-2].body[spectro][
                    "hartmann_left"
                ]
                supervisors[spectro].hartmann_right_status = replies[-2].body[spectro][
                    "hartmann_right"
                ]

            # Check the status of the wago module (wago status)

            wago_telemetry_status_cmd = await command.actor.send_command(
                "lvmieb", f"wago status {spectro}"
            )
            await wago_telemetry_status_cmd

            if wago_telemetry_status_cmd.status.did_fail:
                command.info(
                    text="Failed to receive the telemetry status from wago sensors"
                )
            else:
                replies = wago_telemetry_status_cmd.replies

                supervisors[spectro].rhtRH1 = replies[-2].body[spectro]["rhtRH1"]
                supervisors[spectro].rhtT1 = replies[-2].body[spectro]["rhtT1"]
                supervisors[spectro].rhtRH2 = replies[-2].body[spectro]["rhtRH2"]
                supervisors[spectro].rhtT2 = replies[-2].body[spectro]["rhtT2"]
                supervisors[spectro].rhtRH3 = replies[-2].body[spectro]["rhtRH3"]
                supervisors[spectro].rhtT3 = replies[-2].body[spectro]["rhtT3"]
                supervisors[spectro].rtd1 = replies[-2].body[spectro]["rtd1"]
                supervisors[spectro].rtd2 = replies[-2].body[spectro]["rtd2"]
                supervisors[spectro].rtd3 = replies[-2].body[spectro]["rtd3"]
                supervisors[spectro].rtd4 = replies[-2].body[spectro]["rtd4"]

            # Check the status of the transducer

            transducer_status_cmd = await asyncio.wait_for(
                command.actor.send_command("lvmieb", f"transducer status {spectro}"), 1
            )
            await transducer_status_cmd

            if transducer_status_cmd.status.did_fail:
                command.info(
                    text="Failed to receive the telemetry status from transducer"
                )
            else:
                replies = transducer_status_cmd.replies

                supervisors[spectro].r1_pressure = replies[-2].body[spectro][
                    "r1_pressure"
                ]
                supervisors[spectro].b1_pressure = replies[-2].body[spectro][
                    "b1_pressure"
                ]
                supervisors[spectro].z1_pressure = replies[-2].body[spectro][
                    "z1_pressure"
                ]
                supervisors[spectro].r1_temperature = replies[-2].body[spectro][
                    "r1_temperature"
                ]
                supervisors[spectro].b1_temperature = replies[-2].body[spectro][
                    "b1_temperature"
                ]
                supervisors[spectro].z1_temperature = replies[-2].body[spectro][
                    "z1_temperature"
                ]

            # Check the status of the linear depth gage

            gage_status_cmd = await asyncio.wait_for(
                command.actor.send_command("lvmieb", f"depth status {spectro} z1"), 1
            )
            await gage_status_cmd

            if gage_status_cmd.status.did_fail:
                command.info(
                    text="Failed to receive the telemetry status from transducer"
                )
            else:
                replies = gage_status_cmd.replies

                supervisors[spectro].gage_A = replies[-2].body[spectro]["z1"]["A"]
                supervisors[spectro].gage_B = replies[-2].body[spectro]["z1"]["B"]
                supervisors[spectro].gage_C = replies[-2].body[spectro]["z1"]["C"]

    log.info("status logged successfully!")
    command.info(
        {
            "ARCHON": {
                "STATUS": archon_status,
                "POWER": archon_power_nps,
                "R1_CCD_TEMP": r1ccd_temp,
                "Mod 2 Heater A(r1)": r1heater,
                "B1_CCD_TEMP": b1ccd_temp,
                "Mod 12 Heater A(b1)": b1heater,
                "Z1_CCD_TEMP": z1ccd_temp,
                "Mod 12 Heater B(z1)": z1heater,
            },
            "SHUTTER": {
                "sp1": {
                    "shutter_power_status": supervisors["sp1"].shutter_power_status,
                    "shutter_status": supervisors["sp1"].shutter_status,
                },
                "sp2": {
                    "shutter_power_status": supervisors["sp2"].shutter_power_status,
                    "shutter_status": supervisors["sp2"].shutter_status,
                },
                "sp3": {
                    "shutter_power_status": supervisors["sp3"].shutter_power_status,
                    "shutter_status": supervisors["sp3"].shutter_status,
                },
            },
            "HARTMANN": {
                "sp1": {
                    "hartmann_left_power_status": supervisors[
                        "sp1"
                    ].hartmann_left_power_status,
                    "hartmann_right_power_status": supervisors[
                        "sp1"
                    ].hartmann_right_power_status,
                    "hartmann_left_status": supervisors["sp1"].hartmann_left_status,
                    "hartmann_right_status": supervisors["sp1"].hartmann_right_status,
                },
                "sp2": {
                    "hartmann_left_power_status": supervisors[
                        "sp2"
                    ].hartmann_left_power_status,
                    "hartmann_right_power_status": supervisors[
                        "sp2"
                    ].hartmann_right_power_status,
                    "hartmann_left_status": supervisors["sp2"].hartmann_left_status,
                    "hartmann_right_status": supervisors["sp2"].hartmann_right_status,
                },
                "sp3": {
                    "hartmann_left_power_status": supervisors[
                        "sp3"
                    ].hartmann_left_power_status,
                    "hartmann_right_power_status": supervisors[
                        "sp3"
                    ].hartmann_right_power_status,
                    "hartmann_left_status": supervisors["sp3"].hartmann_left_status,
                    "hartmann_right_status": supervisors["sp3"].hartmann_right_status,
                },
            },
            "IEB": {
                "POWER": {"IEB06": ieb06},
                "HUMIDITY": {
                    "sp1": {
                        "rhtRH1": supervisors["sp1"].rhtRH1,
                        "rhtRH2": supervisors["sp1"].rhtRH2,
                        "rhtRH3": supervisors["sp1"].rhtRH3,
                    },
                    "sp2": {
                        "rhtRH1": supervisors["sp2"].rhtRH1,
                        "rhtRH2": supervisors["sp2"].rhtRH2,
                        "rhtRH3": supervisors["sp2"].rhtRH3,
                    },
                    "sp3": {
                        "rhtRH1": supervisors["sp3"].rhtRH1,
                        "rhtRH2": supervisors["sp3"].rhtRH2,
                        "rhtRH3": supervisors["sp3"].rhtRH3,
                    },
                },
                "TEMPERATURE": {
                    "sp1": {
                        "rhtT1": supervisors["sp1"].rhtT1,
                        "rhtT2": supervisors["sp1"].rhtT2,
                        "rhtT3": supervisors["sp1"].rhtT3,
                        "rtd1": supervisors["sp1"].rtd1,
                        "rtd2": supervisors["sp1"].rtd2,
                        "rtd3": supervisors["sp1"].rtd3,
                        "rtd4": supervisors["sp1"].rtd4,
                    },
                    "sp2": {
                        "rhtT1": supervisors["sp2"].rhtT1,
                        "rhtT2": supervisors["sp2"].rhtT2,
                        "rhtT3": supervisors["sp2"].rhtT3,
                        "rtd1": supervisors["sp2"].rtd1,
                        "rtd2": supervisors["sp2"].rtd2,
                        "rtd3": supervisors["sp2"].rtd3,
                        "rtd4": supervisors["sp2"].rtd4,
                    },
                    "sp3": {
                        "rhtT1": supervisors["sp3"].rhtT1,
                        "rhtT2": supervisors["sp3"].rhtT2,
                        "rhtT3": supervisors["sp3"].rhtT3,
                        "rtd1": supervisors["sp3"].rtd1,
                        "rtd2": supervisors["sp3"].rtd2,
                        "rtd3": supervisors["sp3"].rtd3,
                        "rtd4": supervisors["sp3"].rtd4,
                    },
                },
            },
            "TRANSDUCER": {
                "POWER": {
                    "rasberry_pi_power": rpi,
                    "transducer_power": pres_transducer,
                },
                "TEMPERATURE": {
                    "sp1": {
                        "r1": supervisors["sp1"].r1_temperature,
                        "b1": supervisors["sp1"].b1_temperature,
                        "z1": supervisors["sp1"].z1_temperature,
                    },
                    "sp2": {
                        "r1": supervisors["sp2"].r1_temperature,
                        "b1": supervisors["sp2"].b1_temperature,
                        "z1": supervisors["sp2"].z1_temperature,
                    },
                    "sp3": {
                        "r1": supervisors["sp3"].r1_temperature,
                        "b1": supervisors["sp3"].b1_temperature,
                        "z1": supervisors["sp3"].z1_temperature,
                    },
                },
                "PRESSURE": {
                    "sp1": {
                        "r1": supervisors["sp1"].r1_pressure,
                        "b1": supervisors["sp1"].b1_pressure,
                        "z1": supervisors["sp1"].z1_pressure,
                    },
                    "sp2": {
                        "r1": supervisors["sp2"].r1_pressure,
                        "b1": supervisors["sp2"].b1_pressure,
                        "z1": supervisors["sp2"].z1_pressure,
                    },
                    "sp3": {
                        "r1": supervisors["sp3"].r1_pressure,
                        "b1": supervisors["sp3"].b1_pressure,
                        "z1": supervisors["sp3"].z1_pressure,
                    },
                },
            },
            "ARC_LAMP": {
                "ARGON": argon,
                "XENON": xenon,
                "HGAR": hgar,
                "LDLS": ldls,
                "KRYPTON": krypton,
                "NEON": neon,
                "HGNE": hgne,
            },
            "LN2VALVE": {"LN2NIR": ln2nir, "LN2RED": ln2red},
            "TESTCCD": supervisors["sp1"].testccd,
            "LINEARGAGE": {
                "sp1": {
                    supervisors["sp1"].testccd: {
                        "A": supervisors["sp1"].gage_A,
                        "B": supervisors["sp1"].gage_B,
                        "C": supervisors["sp1"].gage_C,
                    }
                }
            },
        }
    )

    return command.finish()


def convert(flag: bool):
    if flag:
        return "ON"
    else:
        return "OFF"
