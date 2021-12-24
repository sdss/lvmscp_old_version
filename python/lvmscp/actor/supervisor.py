import asyncio
import datetime
import logging

from clu import Command

from sdsstools import get_logger


# logging
log = get_logger("sdss-lvmscp")

log.sh.setLevel(logging.DEBUG)


class Supervisor:
    """This is the class that has the telemetry data and functions
    of each spectrograph sp1, sp2, sp3.
    This class will be instantiated and run with the actor.
    Each spectrograph sp1, sp2, sp3 will have
    instance of this Supervisor class, controlling the variables
    """

    def __init__(self, spectro: str):

        # Now only sp1 spectrograph is available 20211224
        if spectro == "sp1":
            self.ready = True
            self.name = spectro
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
            self.gage_A = "ERROR"
            self.gage_B = "ERROR"
            self.gage_C = "ERROR"
            self.testccd = "z1"
            self.ln2nir = "ERROR"
            self.ln2red = "ERROR"
            self.archon_power_nps = "ERROR"
            self.argon = "ERROR"
            self.xenon = "ERROR"
            self.hgar = "ERROR"
            self.ldls = "ERROR"
            self.krypton = "ERROR"
            self.neon = "ERROR"
            self.hgne = "ERROR"
            self.ieb06 = "ERROR"
            self.rpi = "ERROR"
            self.pres_transducer = "ERROR"
            self.archon_status = "ERROR"
            self.r1ccd_temp = "ERROR"
            self.b1ccd_temp = "ERROR"
            self.z1ccd_temp = "ERROR"
            self.r1heater = "ERROR"
            self.b1heater = "ERROR"
            self.z1heater = "ERROR"
            self.status_dict = {}
        # sp2 and sp3 spectrograph is unavailable now. 20211224
        elif spectro == "sp2":
            self.ready = False
            self.name = spectro
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
            self.gage_A = "Not Connected"
            self.gage_B = "Not Connected"
            self.gage_C = "Not Connected"
            self.testccd = "Not connected"
            self.ln2nir = "Not connected"
            self.ln2red = "Not connected"
            self.archon_power_nps = "Not connected"
            self.argon = "Not connected"
            self.xenon = "Not connected"
            self.hgar = "Not connected"
            self.ldls = "Not connected"
            self.krypton = "Not connected"
            self.neon = "Not connected"
            self.hgne = "Not connected"
            self.ieb06 = "Not connected"
            self.rpi = "Not connected"
            self.pres_transducer = "Not connected"
            self.archon_status = "Not connected"
            self.r1ccd_temp = "Not connected"
            self.b1ccd_temp = "Not connected"
            self.z1ccd_temp = "Not connected"
            self.r1heater = "Not connected"
            self.b1heater = "Not connected"
            self.z1heater = "Not connected"
            self.status_dict = {}
        elif spectro == "sp3":
            self.ready = False
            self.name = spectro
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
            self.gage_A = "Not Connected"
            self.gage_B = "Not Connected"
            self.gage_C = "Not Connected"
            self.testccd = "Not connected"
            self.ln2nir = "Not connected"
            self.ln2red = "Not connected"
            self.archon_power_nps = "Not connected"
            self.argon = "Not connected"
            self.xenon = "Not connected"
            self.hgar = "Not connected"
            self.ldls = "Not connected"
            self.krypton = "Not connected"
            self.neon = "Not connected"
            self.hgne = "Not connected"
            self.ieb06 = "Not connected"
            self.rpi = "Not connected"
            self.pres_transducer = "Not connected"
            self.archon_status = "Not connected"
            self.r1ccd_temp = "Not connected"
            self.b1ccd_temp = "Not connected"
            self.z1ccd_temp = "Not connected"
            self.r1heater = "Not connected"
            self.b1heater = "Not connected"
            self.z1heater = "Not connected"
            self.status_dict = {}

    async def UpdateStatus(self, command: Command):
        """updates the parameters of the spectrograph.
        The variables are all member variables of the Supervisor instance,
        and updated when this function is called.

        Args:
            command (Command): this is the Command instance for actor commanding.
            Since we update the status of the lvmscp actor by sending commands
            to lower level actors (lvmieb, archon), the command instance
            will use the send_command method to send commands to lower level.
        """

        log.info(f"{pretty(datetime.datetime.now())} | before lvmscp update")

        # check the status of archon controller
        archon_status_cmd = await command.actor.send_command("archon", "status")
        await archon_status_cmd

        if archon_status_cmd.status.did_fail:
            command.info(text="Failed to receive the status from archon")
            pass
        else:
            # more information can be added here
            replies = archon_status_cmd.replies
            self.archon_status = replies[-2].body["status"]["status_names"]
            self.r1ccd_temp = replies[-2].body["status"]["mod2/tempa"]
            self.b1ccd_temp = replies[-2].body["status"]["mod12/tempb"]
            self.z1ccd_temp = replies[-2].body["status"]["mod12/tempa"]
            self.r1heater = replies[-2].body["status"]["mod2/heateraoutput"]
            self.b1heater = replies[-2].body["status"]["mod12/heateraoutput"]
            self.z1heater = replies[-2].body["status"]["mod12/heaterboutput"]

        # check the ready value of the spectrograpgh Supervisor instance
        if self.ready:
            # Check the wago power module from lvmieb
            wago_power_status_cmd = await command.actor.send_command(
                "lvmieb", f"wago getpower {self.name}"
            )
            await wago_power_status_cmd

            if wago_power_status_cmd.status.did_fail:
                command.info(text="Failed to receive the power status from wago relays")
            else:
                replies = wago_power_status_cmd.replies
                self.shutter_power_status = replies[-2].body[self.name]["shutter_power"]
                self.hartmann_left_power_status = replies[-2].body[self.name][
                    "hartmann_left_power"
                ]
                self.hartmann_right_power_status = replies[-2].body[self.name][
                    "hartmann_right_power"
                ]

            # Check the status (opened / closed) of the shutter from lvmieb
            shutter_status_cmd = await command.actor.send_command(
                "lvmieb", f"shutter status {self.name}"
            )
            await shutter_status_cmd

            if shutter_status_cmd.status.did_fail:
                command.info(text="Failed to receive the status of the shutter status")
            else:
                replies = shutter_status_cmd.replies
                self.shutter_status = replies[-2].body[self.name]["shutter"]

            # Check the status (opened / closed) of the hartmann doors from lvmieb
            hartmann_status_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann status {self.name}"
            )
            await hartmann_status_cmd

            if hartmann_status_cmd.status.did_fail:
                command.info(text="Failed to receive the status of the hartmann status")
            else:
                replies = hartmann_status_cmd.replies
                self.hartmann_left_status = replies[-2].body[self.name]["hartmann_left"]
                self.hartmann_right_status = replies[-2].body[self.name][
                    "hartmann_right"
                ]

            # Check the status of the wago sensor module (wago status)
            wago_telemetry_status_cmd = await command.actor.send_command(
                "lvmieb", f"wago status {self.name}"
            )
            await wago_telemetry_status_cmd

            if wago_telemetry_status_cmd.status.did_fail:
                command.info(
                    text="Failed to receive the telemetry status from wago sensors"
                )
            else:
                replies = wago_telemetry_status_cmd.replies

                self.rhtRH1 = replies[-2].body[self.name]["rhtRH1"]
                self.rhtT1 = replies[-2].body[self.name]["rhtT1"]
                self.rhtRH2 = replies[-2].body[self.name]["rhtRH2"]
                self.rhtT2 = replies[-2].body[self.name]["rhtT2"]
                self.rhtRH3 = replies[-2].body[self.name]["rhtRH3"]
                self.rhtT3 = replies[-2].body[self.name]["rhtT3"]
                self.rtd1 = replies[-2].body[self.name]["rtd1"]
                self.rtd2 = replies[-2].body[self.name]["rtd2"]
                self.rtd3 = replies[-2].body[self.name]["rtd3"]
                self.rtd4 = replies[-2].body[self.name]["rtd4"]

            # Check the status of the transducer
            transducer_status_cmd = await asyncio.wait_for(
                command.actor.send_command("lvmieb", f"transducer status {self.name}"),
                1,
            )
            await transducer_status_cmd

            if transducer_status_cmd.status.did_fail:
                command.info(
                    text="Failed to receive the telemetry status from transducer"
                )
            else:
                replies = transducer_status_cmd.replies

                self.r1_pressure = replies[-2].body[self.name]["r1_pressure"]
                self.b1_pressure = replies[-2].body[self.name]["b1_pressure"]
                self.z1_pressure = replies[-2].body[self.name]["z1_pressure"]
                self.r1_temperature = replies[-2].body[self.name]["r1_temperature"]
                self.b1_temperature = replies[-2].body[self.name]["b1_temperature"]
                self.z1_temperature = replies[-2].body[self.name]["z1_temperature"]

            # Check the status of the linear depth gage
            gage_status_cmd = await asyncio.wait_for(
                command.actor.send_command("lvmieb", f"depth status {self.name} z1"), 1
            )
            await gage_status_cmd

            if gage_status_cmd.status.did_fail:
                command.info(
                    text="Failed to receive the telemetry status from transducer"
                )
            else:
                replies = gage_status_cmd.replies

            # repeat the status command if the A value is wrong.
            # A value is not updated frequently due to hardware connection
            if replies[-2].body[self.name]["z1"]["A"] == -999.0:
                gage_status_cmd = await asyncio.wait_for(
                    command.actor.send_command(
                        "lvmieb", f"depth status {self.name} z1"
                    ),
                    1,
                )
                await gage_status_cmd

                if gage_status_cmd.status.did_fail:
                    command.info(
                        text="Failed to receive the telemetry status from transducer"
                    )
                else:
                    replies = gage_status_cmd.replies

            self.gage_A = replies[-2].body[self.name]["z1"]["A"]
            self.gage_B = replies[-2].body[self.name]["z1"]["B"]
            self.gage_C = replies[-2].body[self.name]["z1"]["C"]

        log.info(f"{pretty(datetime.datetime.now())} | after lvmscp update")
        return


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
