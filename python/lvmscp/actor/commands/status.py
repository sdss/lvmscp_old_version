import asyncio
import logging

from clu.command import Command

from sdsstools import get_logger

from . import parser


# logging
log = get_logger("sdss-lvmscp")

log.sh.setLevel(logging.DEBUG)

spectro_list = ["sp1", "sp2", "sp3"]


@parser.command()
async def status(command: Command):
    """Receive all of the telemetry related to the spectrograph"""
    # check the power of the network power switch

    nps_status_cmd = await command.actor.send_command("lvmnps", "status all")
    await nps_status_cmd

    if nps_status_cmd.status.did_fail:
        command.info(text="Failed to receive the power status from wago relays")
    else:
        replies = nps_status_cmd.replies

    ln2nir = convert(replies[-2].body["STATUS"]["DLI-NPS-02"]["LN2 NIR valve"]["STATE"])
    ln2red = convert(replies[-2].body["STATUS"]["DLI-NPS-02"]["LN2 Red Valve"]["STATE"])

    archon_power_nps = convert(
        replies[-2].body["STATUS"]["DLI-NPS-02"]["LVM-Archon-02"]["STATE"]
    )

    argon = convert(replies[-2].body["STATUS"]["DLI-NPS-03"]["Argon"]["STATE"])
    xenon = convert(replies[-2].body["STATUS"]["DLI-NPS-03"]["Xenon"]["STATE"])
    hgar = convert(replies[-2].body["STATUS"]["DLI-NPS-03"]["Hg (Ar)"]["STATE"])
    ldls = convert(replies[-2].body["STATUS"]["DLI-NPS-03"]["LDLS"]["STATE"])
    krypton = convert(replies[-2].body["STATUS"]["DLI-NPS-03"]["Krypton"]["STATE"])
    neon = convert(replies[-2].body["STATUS"]["DLI-NPS-03"]["Neon"]["STATE"])
    hgne = convert(replies[-2].body["STATUS"]["DLI-NPS-03"]["Hg (Ne)"]["STATE"])

    ieb06 = convert(replies[-2].body["STATUS"]["DLI-NPS-02"]["IEB06"]["STATE"])

    rpi = convert(replies[-2].body["STATUS"]["DLI-NPS-02"]["RPi"]["STATE"])
    pres_transducer = convert(
        replies[-2].body["STATUS"]["DLI-NPS-02"]["Pressure transducers"]["STATE"]
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

    spec_dict = {}

    for spectro in spectro_list:

        # check the power of the shutter & hartmann doors
        spec_dict[spectro] = spectro_data(spectro)

        if spec_dict[spectro].ready:
            wago_power_status_cmd = await command.actor.send_command(
                "lvmieb", f"wago getpower {spectro}"
            )
            await wago_power_status_cmd

            if wago_power_status_cmd.status.did_fail:
                command.info(text="Failed to receive the power status from wago relays")
            else:
                replies = wago_power_status_cmd.replies
                spec_dict[spectro].shutter_power_status = replies[-2].body[spectro][
                    "shutter_power"
                ]
                spec_dict[spectro].hartmann_left_power_status = replies[-2].body[
                    spectro
                ]["hartmann_left_power"]
                spec_dict[spectro].hartmann_right_power_status = replies[-2].body[
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
                spec_dict[spectro].shutter_status = replies[-2].body[spectro]["shutter"]

            # Check the status (opened / closed) of the hartmann doors

            hartmann_status_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann status {spectro}"
            )
            await hartmann_status_cmd

            if hartmann_status_cmd.status.did_fail:
                command.info(text="Failed to receive the status of the hartmann status")
            else:
                replies = hartmann_status_cmd.replies
                spec_dict[spectro].hartmann_left_status = replies[-2].body[spectro][
                    "hartmann_left"
                ]
                spec_dict[spectro].hartmann_right_status = replies[-2].body[spectro][
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

                spec_dict[spectro].rhtRH1 = replies[-2].body[spectro]["rhtRH1"]
                spec_dict[spectro].rhtT1 = replies[-2].body[spectro]["rhtT1"]
                spec_dict[spectro].rhtRH2 = replies[-2].body[spectro]["rhtRH2"]
                spec_dict[spectro].rhtT2 = replies[-2].body[spectro]["rhtT2"]
                spec_dict[spectro].rhtRH3 = replies[-2].body[spectro]["rhtRH3"]
                spec_dict[spectro].rhtT3 = replies[-2].body[spectro]["rhtT3"]
                spec_dict[spectro].rtd1 = replies[-2].body[spectro]["rtd1"]
                spec_dict[spectro].rtd2 = replies[-2].body[spectro]["rtd2"]
                spec_dict[spectro].rtd3 = replies[-2].body[spectro]["rtd3"]
                spec_dict[spectro].rtd4 = replies[-2].body[spectro]["rtd4"]

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

                spec_dict[spectro].r1_pressure = replies[-2].body[spectro][
                    "r1_pressure"
                ]
                spec_dict[spectro].b1_pressure = replies[-2].body[spectro][
                    "b1_pressure"
                ]
                spec_dict[spectro].z1_pressure = replies[-2].body[spectro][
                    "z1_pressure"
                ]
                spec_dict[spectro].r1_temperature = replies[-2].body[spectro][
                    "r1_temperature"
                ]
                spec_dict[spectro].b1_temperature = replies[-2].body[spectro][
                    "b1_temperature"
                ]
                spec_dict[spectro].z1_temperature = replies[-2].body[spectro][
                    "z1_temperature"
                ]

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
                    "shutter_power_status": spec_dict["sp1"].shutter_power_status,
                    "shutter_status": spec_dict["sp1"].shutter_status,
                },
                "sp2": {
                    "shutter_power_status": spec_dict["sp2"].shutter_power_status,
                    "shutter_status": spec_dict["sp2"].shutter_status,
                },
                "sp3": {
                    "shutter_power_status": spec_dict["sp3"].shutter_power_status,
                    "shutter_status": spec_dict["sp3"].shutter_status,
                },
            },
            "HARTMANN": {
                "sp1": {
                    "hartmann_left_power_status": spec_dict[
                        "sp1"
                    ].hartmann_left_power_status,
                    "hartmann_right_power_status": spec_dict[
                        "sp1"
                    ].hartmann_right_power_status,
                    "hartmann_left_status": spec_dict["sp1"].hartmann_left_status,
                    "hartmann_right_status": spec_dict["sp1"].hartmann_right_status,
                },
                "sp2": {
                    "hartmann_left_power_status": spec_dict[
                        "sp2"
                    ].hartmann_left_power_status,
                    "hartmann_right_power_status": spec_dict[
                        "sp2"
                    ].hartmann_right_power_status,
                    "hartmann_left_status": spec_dict["sp2"].hartmann_left_status,
                    "hartmann_right_status": spec_dict["sp2"].hartmann_right_status,
                },
                "sp3": {
                    "hartmann_left_power_status": spec_dict[
                        "sp3"
                    ].hartmann_left_power_status,
                    "hartmann_right_power_status": spec_dict[
                        "sp3"
                    ].hartmann_right_power_status,
                    "hartmann_left_status": spec_dict["sp3"].hartmann_left_status,
                    "hartmann_right_status": spec_dict["sp3"].hartmann_right_status,
                },
            },
            "IEB": {
                "POWER": {"IEB06": ieb06},
                "HUMIDITY": {
                    "sp1": {
                        "rhtRH1": spec_dict["sp1"].rhtRH1,
                        "rhtRH2": spec_dict["sp1"].rhtRH2,
                        "rhtRH3": spec_dict["sp1"].rhtRH3,
                    },
                    "sp2": {
                        "rhtRH1": spec_dict["sp2"].rhtRH1,
                        "rhtRH2": spec_dict["sp2"].rhtRH2,
                        "rhtRH3": spec_dict["sp2"].rhtRH3,
                    },
                    "sp3": {
                        "rhtRH1": spec_dict["sp3"].rhtRH1,
                        "rhtRH2": spec_dict["sp3"].rhtRH2,
                        "rhtRH3": spec_dict["sp3"].rhtRH3,
                    },
                },
                "TEMPERATURE": {
                    "sp1": {
                        "rhtT1": spec_dict["sp1"].rhtT1,
                        "rhtT2": spec_dict["sp1"].rhtT2,
                        "rhtT3": spec_dict["sp1"].rhtT3,
                        "rtd1": spec_dict["sp1"].rtd1,
                        "rtd2": spec_dict["sp1"].rtd2,
                        "rtd3": spec_dict["sp1"].rtd3,
                        "rtd4": spec_dict["sp1"].rtd4,
                    },
                    "sp2": {
                        "rhtT1": spec_dict["sp2"].rhtT1,
                        "rhtT2": spec_dict["sp2"].rhtT2,
                        "rhtT3": spec_dict["sp2"].rhtT3,
                        "rtd1": spec_dict["sp2"].rtd1,
                        "rtd2": spec_dict["sp2"].rtd2,
                        "rtd3": spec_dict["sp2"].rtd3,
                        "rtd4": spec_dict["sp2"].rtd4,
                    },
                    "sp3": {
                        "rhtT1": spec_dict["sp3"].rhtT1,
                        "rhtT2": spec_dict["sp3"].rhtT2,
                        "rhtT3": spec_dict["sp3"].rhtT3,
                        "rtd1": spec_dict["sp3"].rtd1,
                        "rtd2": spec_dict["sp3"].rtd2,
                        "rtd3": spec_dict["sp3"].rtd3,
                        "rtd4": spec_dict["sp3"].rtd4,
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
                        "r1": spec_dict["sp1"].r1_temperature,
                        "b1": spec_dict["sp1"].b1_temperature,
                        "z1": spec_dict["sp1"].z1_temperature,
                    },
                    "sp2": {
                        "r1": spec_dict["sp2"].r1_temperature,
                        "b1": spec_dict["sp2"].b1_temperature,
                        "z1": spec_dict["sp2"].z1_temperature,
                    },
                    "sp3": {
                        "r1": spec_dict["sp3"].r1_temperature,
                        "b1": spec_dict["sp3"].b1_temperature,
                        "z1": spec_dict["sp3"].z1_temperature,
                    },
                },
                "PRESSURE": {
                    "sp1": {
                        "r1": spec_dict["sp1"].r1_pressure,
                        "b1": spec_dict["sp1"].b1_pressure,
                        "z1": spec_dict["sp1"].z1_pressure,
                    },
                    "sp2": {
                        "r1": spec_dict["sp2"].r1_pressure,
                        "b1": spec_dict["sp2"].b1_pressure,
                        "z1": spec_dict["sp2"].z1_pressure,
                    },
                    "sp3": {
                        "r1": spec_dict["sp3"].r1_pressure,
                        "b1": spec_dict["sp3"].b1_pressure,
                        "z1": spec_dict["sp3"].z1_pressure,
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
        }
    )
    return command.finish()


def convert(flag: bool):
    if flag:
        return "ON"
    else:
        return "OFF"


class spectro_data:
    def __init__(self, spectro: str):

        # check the availabilty of the spectrograph
        if spectro == "sp1":
            self.ready = True
            self.spectro = spectro
            self.shutter_status = "ERROR"
            self.shutter_power_status = "ERROR"
            self.hartmann_left_status = "ERROR"
            self.hartmann_right_status = "ERROR"
            self.hartmann_left_power_status = "ERROR"
            self.hartmann_right_power_status = "ERROR"
            self.rhtRH1 = "ERROR"
            self.rhtT1 = "ERROR"
            self.rhtRH2 = "ERROR"
            self.rhtT2 = "ERROR"
            self.rhtRH3 = "ERROR"
            self.rhtT3 = "ERROR"
            self.rtd1 = "ERROR"
            self.rtd2 = "ERROR"
            self.rtd3 = "ERROR"
            self.rtd4 = "ERROR"
            self.r1_pressure = "ERROR"
            self.b1_pressure = "ERROR"
            self.z1_pressure = "ERROR"
            self.r1_temperature = "ERROR"
            self.b1_temperature = "ERROR"
            self.z1_temperature = "ERROR"
        else:
            self.ready = False
            self.shutter_status = "Not Connected"
            self.shutter_power_status = "Not Connected"
            self.hartmann_left_status = "Not Connected"
            self.hartmann_right_status = "Not Connected"
            self.hartmann_left_power_status = "Not Connected"
            self.hartmann_right_power_status = "Not Connected"
            self.rhtRH1 = "Not Connected"
            self.rhtT1 = "Not Connected"
            self.rhtRH2 = "Not Connected"
            self.rhtT2 = "Not Connected"
            self.rhtRH3 = "Not Connected"
            self.rhtT3 = "Not Connected"
            self.rtd1 = "Not Connected"
            self.rtd2 = "Not Connected"
            self.rtd3 = "Not Connected"
            self.rtd4 = "Not Connected"
            self.r1_pressure = "Not Connected"
            self.b1_pressure = "Not Connected"
            self.z1_pressure = "Not Connected"
            self.r1_temperature = "Not Connected"
            self.b1_temperature = "Not Connected"
            self.z1_temperature = "Not Connected"
