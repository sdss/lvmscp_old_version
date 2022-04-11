import asyncio
import datetime
import json
import logging

import click
from clu import Command

from sdsstools import get_logger

from lvmscp.exceptions import lvmscpError


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
        self.exposure_lock = asyncio.Lock()
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
            self.nirled = "ERROR"
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
            self.readoutmode = "800"  # default readout mode is 800 MHz
            self.status_dict = {}
            self.labtemp = -999
            self.labhum = "ERROR"
        # sp2 and sp3 spectrograph is unavailable now. 20210117
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
            self.nirled = "Not connected"
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
            self.readoutmode = "Not connected"
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
            self.nirled = "Not connected"
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
            self.readoutmode = "Not connected"
            self.status_dict = {}

    async def UpdateStatus(self, command: Command):
        """
        updates the parameters of the spectrograph.
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
            # 20220331 there was an error that the replies[-2].body[self.name]["z1"] reports False,
            # so I added some if condition for the unfrequent update of the hardware connection

            print(replies[-2].body[self.name]["z1"])
            if replies[-2].body[self.name]["z1"] is not False:
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

            # check the status of the lab temperature & lab humidity
            self.labtemp, self.labhum = await self.read_govee(command)
            print(self.labtemp, self.labhum)

        log.info(f"{pretty(datetime.datetime.now())} | after lvmscp update")
        return

    async def UpdatePowerStatus(self, command: Command):

        nps_status_cmd = await command.actor.send_command("lvmnps", "status")
        await nps_status_cmd

        if nps_status_cmd.status.did_fail:
            command.info(text="Failed to receive the power status from power switch")
        else:
            replies = nps_status_cmd.replies
        self.ln2nir = convert(
            replies[-2].body["status"]["DLI-02"]["LN2 NIR Valve"]["state"]
        )
        self.ln2red = convert(
            replies[-2].body["status"]["DLI-02"]["LN2 Red Valve"]["state"]
        )

        self.archon_power_nps = convert(
            replies[-2].body["status"]["DLI-02"]["LVM-Archon-02"]["state"]
        )

        self.argon = convert(replies[-2].body["status"]["DLI-03"]["Argon"]["state"])
        self.xenon = convert(replies[-2].body["status"]["DLI-03"]["Xenon"]["state"])
        self.hgar = convert(replies[-2].body["status"]["DLI-03"]["Hg (Ar)"]["state"])
        self.ldls = convert(replies[-2].body["status"]["DLI-03"]["LDLS"]["state"])
        self.krypton = convert(replies[-2].body["status"]["DLI-03"]["Krypton"]["state"])
        self.neon = convert(replies[-2].body["status"]["DLI-03"]["Neon"]["state"])
        self.hgne = convert(replies[-2].body["status"]["DLI-03"]["Hg (Ne)"]["state"])
        self.nirled = convert(replies[-2].body["status"]["DLI-03"]["NIR LED"]["state"])

        self.ieb06 = convert(replies[-2].body["status"]["DLI-02"]["IEB06"]["state"])

        self.rpi = convert(replies[-2].body["status"]["DLI-02"]["RPi"]["state"])
        self.pres_transducer = convert(
            replies[-2].body["status"]["DLI-02"]["Pressure transducers"]["state"]
        )

        log.info(
            f"{pretty(datetime.datetime.now())} | after lamp info update from lvmnps"
        )
        return

    async def SetHartmann(self, command: Command, request):

        await self.UpdateStatus(command)

        # Makes the status only the right door opened
        if request == "right":
            if self.hartmann_right_status == "closed":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann open {self.name} --side={request}"
                )
                await open_cmd
            elif self.hartmann_right_status == "opened":
                command.info(text=f"{request} already opened")

            if self.hartmann_left_status == "opened":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann close {self.name} --side=left"
                )
                await open_cmd
        elif request == "left":
            if self.hartmann_left_status == "closed":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann open {self.name} --side={request}"
                )
                await open_cmd
            elif self.hartmann_left_status == "opened":
                command.info(text=f"{request} already opened")

            if self.hartmann_right_status == "opened":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann close {self.name} --side=right"
                )
                await open_cmd
        elif request == "both":
            if self.hartmann_right_status == "closed":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann open {self.name} --side=right"
                )
                await open_cmd
            elif self.hartmann_right_status == "opened":
                command.info(text="right already opened")

            if self.hartmann_left_status == "closed":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann open {self.name} --side=left"
                )
                await open_cmd
            elif self.hartmann_left_status == "opened":
                command.info(text="left already opened")
        elif request == "close":
            if self.hartmann_right_status == "closed":
                command.info(text="right already closed")
            elif self.hartmann_right_status == "opened":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann close {self.name} --side=right"
                )
                await open_cmd

            if self.hartmann_left_status == "closed":
                command.info(text="left already closed")
            elif self.hartmann_left_status == "opened":
                open_cmd = await command.actor.send_command(
                    "lvmieb", f"hartmann close {self.name} --side=left"
                )
                await open_cmd

        await self.UpdateStatus(command)

        log.info(
            f"{pretty(datetime.datetime.now())} | after lamp info update from lvmnps"
        )
        return

    async def SetReadout(self, command: Command, readout):

        self.readoutmode = readout
        if readout == "400":
            try:
                archon_status_cmd = await command.actor.send_command(
                    "archon", "init lvm/config/archon/LVM_400MHz.acf"
                )
                await archon_status_cmd
            except lvmscpError as err:
                command.fail(error=str(err))
        elif readout == "800":
            try:
                archon_status_cmd = await command.actor.send_command(
                    "archon", "init lvm/config/archon/LVM_800MHz.acf"
                )
                await archon_status_cmd
            except lvmscpError as err:
                command.fail(error=str(err))
        elif readout == "HDR":
            try:
                archon_status_cmd = await command.actor.send_command(
                    "archon", "init --hdr"
                )
                await archon_status_cmd
            except lvmscpError as err:
                command.fail(error=str(err))

        if archon_status_cmd.status.did_fail:
            command.fail(text=archon_status_cmd.status)

        return

    async def exposure(
        self,
        command: Command,
        exptime: float,
        count: int,
        flavour: str,
        binning=1,
        flush="no",
        header="{}",
    ):

        data_directory = []
        spectro = self.name

        # Check the exposure time input (bias = 0.0)
        log.debug(f"{pretty(datetime.datetime.now())} | Checking exposure time")
        if flavour != "bias" and exptime is None:
            log.error(f"{pretty(datetime.datetime.now())} | EXPOSURE-TIME is required.")
            raise click.UsageError("EXPOSURE-TIME is required unless --flavour=bias.")
        elif flavour == "bias":
            exptime = 0.0

        if exptime < 0.0:
            log.error(
                f"{pretty(datetime.datetime.now())} | EXPOSURE-TIME cannot be negative"
            )
            raise click.UsageError("EXPOSURE-TIME cannot be negative")

        # lock for exposure sequence only running for one delegate
        async with self.exposure_lock:

            # pinging lower actors
            log.debug(f"{pretty(datetime.datetime.now())} | Pinging lower actors . . .")
            command.info(text="Pinging . . .")

            err = await check_actor_ping(command, "lvmnps")
            if err is True:
                log.info(f"{pretty(datetime.datetime.now())} | lvmnps OK!")
                command.info(text="lvmnps OK!")
            else:
                log.error(f"{pretty(datetime.datetime.now())} | {err}")
                raise click.UsageError(err)

            err = await check_actor_ping(command, "archon")
            if err is True:
                log.info(f"{pretty(datetime.datetime.now())} | archon OK!")
                command.info(text="archon OK!")
            else:
                log.error(f"{pretty(datetime.datetime.now())} | {err}")
                raise click.UsageError(err)

            err = await check_actor_ping(command, "lvmieb")
            if err is True:
                log.info(f"{pretty(datetime.datetime.now())} | lvmieb OK!")
                command.info(text="lvmieb OK!")
            else:
                log.error(f"{pretty(datetime.datetime.now())} | {err}")
                raise click.UsageError(err)

            await self.UpdateStatus(command)

            if flavour != "test":

                if self.shutter_power_status == "OFF":
                    raise click.UsageError(
                        "Cannot start exposure : Exposure shutter power off"
                    )
                elif self.hartmann_left_power_status == "OFF":
                    raise click.UsageError(
                        "Cannot start exposure : Left hartmann door power off"
                    )
                elif self.hartmann_right_power_status == "OFF":
                    raise click.UsageError(
                        "Cannot start exposure : Right hartmann door power off"
                    )
                elif self.shutter_status != "closed":
                    raise click.UsageError(
                        "Shutter is already opened. The command will fail"
                    )

            # when the flavour is object
            if flavour == "object":
                # Check the hartmann door is all opened for the science exposure
                log.debug(
                    f"{pretty(datetime.datetime.now())} | Checking hartmann opened . . ."
                )
                command.info(text="Checking hartmann opened . . .")
                await self.UpdateStatus(command)
                if not (
                    self.hartmann_left_status == "opened"
                    and self.hartmann_right_status == "opened"  # noqa E501
                ):
                    raise click.UsageError(
                        "Hartmann doors are not opened for the science exposure"
                    )

            # Check the archon controller is initialized and on the status of IDLE
            log.debug(
                f"{pretty(datetime.datetime.now())} | Checking archon controller initialized . . ."
            )
            command.info(text="Checking archon controller initialized . . .")
            print(self.archon_status[0])
            if self.archon_status[0] != "IDLE":
                raise click.UsageError("archon is not initialized")

            # Check the status of lamps for arc exposure
            check_lamp = None
            if flavour == "arc":
                log.debug(
                    f"{pretty(datetime.datetime.now())} | Checking arc lamps . . ."
                )
                command.info(text="Checking arc lamps . . .")

                try:
                    check_lamp = await self.check_arc_lamp(command)
                except Exception as err:
                    log.error(f"{pretty(datetime.datetime.now())} | {err}")
                    raise click.UsageError(err)

                if not check_lamp:
                    raise click.UsageError("arc lamps are all off . . .")

            # starting the exposure
            log.info(f"{pretty(datetime.datetime.now())} | Starting the exposure.")
            command.info(text="Starting the exposure.")
            # start exposure loop
            for nn in range(count):

                log.info(
                    f"{pretty(datetime.datetime.now())} | Taking exposure {nn + 1} of {count}."
                )
                # command.info(text=f"Taking exposure {nn + 1} of {count}.")
                # receive the telemetry data to add on the FIT header
                header_json = await self.extra_header_telemetry(
                    command, header, flavour
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
                            raise click.UsageError("Failed flushing")

                # Start CCD exposure
                log.info(
                    f"{pretty(datetime.datetime.now())} | Start CCD exposure . . ."
                )

                # archon has to send flavour flat for arc lamps
                if flavour == "arc":
                    flavour = "flat"

                # send exposure command to archon

                # for test image type, you have to send as 'object' to archon
                if flavour == "test":
                    archon_cmd = await (
                        await command.actor.send_command(
                            "archon",
                            f"expose start --controller {spectro} --object --binning {binning} {exptime}",  # noqa E501
                        )
                    )
                else:
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
                    raise click.UsageError(
                        "Failed starting exposure. Trying to abort and exiting."
                    )
                else:
                    reply = archon_cmd.replies
                    log.debug(
                        f"{pretty(datetime.datetime.now())} | {reply[-2].body['text']}"
                    )
                    command.info(text=reply[-2].body["text"])

                # opening the shutter for arc and object type frame
                if (
                    flavour != "bias" and flavour != "dark" and flavour != "test"
                ) and exptime > 0:
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
                        await command.actor.send_command(
                            "archon", "expose abort --flush"
                        )
                        log.error(
                            f"{pretty(datetime.datetime.now())} | Shutter failed to open"
                        )
                        raise click.UsageError("Shutter failed to open")

                    # Report status of the shutter
                    await self.UpdateStatus(command)
                    if self.shutter_status not in ["opened", "closed"]:
                        log.error(
                            f"{pretty(datetime.datetime.now())} | Unknown shutter status {self.shutter_status}."  # noqa E501
                        )
                        raise click.UsageError(
                            f"Unknown shutter status {self.shutter_status}."
                        )
                    log.info(
                        f"{pretty(datetime.datetime.now())} | Shutter: {self.shutter_status}."
                    )
                    command.info(text=f"Shutter is now {self.shutter_status}.")

                    if not (
                        await asyncio.create_task(
                            close_shutter_after(command, exptime, spectro)
                        )
                    ):
                        await command.actor.send_command(
                            "archon", "expose abort --flush"
                        )
                        log.error(
                            f"{pretty(datetime.datetime.now())} | Failed to close the shutter"
                        )
                        raise click.UsageError("Failed to close the shutter")
                # dark frame doesn't have to open the shutter
                elif flavour == "dark" and flavour == "test":
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
                    raise click.UsageError("Failed reading out exposure")

                else:
                    # wait until the status of the archon changes into IDLE
                    while True:
                        readout_cmd = await command.actor.send_command(
                            "archon", "status"
                        )
                        await readout_cmd
                        readout_replies = readout_cmd.replies
                        archon_readout = readout_replies[-2].body["status"][
                            "status_names"
                        ][0]
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
            return data_directory

    async def check_arc_lamp(self, command):
        """Check the arc lamp status

        Args:
            command ([type]): [description]

        Returns:
            [type]: [description]
        """
        await self.UpdatePowerStatus(command)

        check_lamp = {
            "ARGON": self.argon,
            "XENON": self.xenon,
            "HGAR": self.hgar,
            "LDLS": self.ldls,
            "KRYPTON": self.krypton,
            "NEON": self.neon,
            "HGNE": self.hgne,
            "NIRLED": self.nirled,
        }

        sum = 0

        for key, value in check_lamp.items():
            if value == "ON":
                sum = sum + 1
                command.info(text=f"{key} flat lamp is on!")

        if sum == 0:
            return False

        return check_lamp

    async def extra_header_telemetry(self, command, header: str, flavour):
        """telemetry from the devices and add it on the header

        Args:
            command ([type]): [description]
            header (str): [description]

        Returns:
            [type]: [description]
        """

        await self.UpdateStatus(command)
        check_lamp = await self.check_arc_lamp(command)

        left = -1
        if self.hartmann_left_status == "opened":
            left = 0
        elif self.hartmann_left_status == "closed":
            left = 1

        right = -1
        if self.hartmann_right_status == "opened":
            right = 0
        elif self.hartmann_right_status == "closed":
            right = 1

        header_dict = {
            "rhtRH1": (self.rhtRH1, "IEB rht sensor humidity [%]"),
            "rhtRH2": (self.rhtRH2, "IEB rht sensor humidity [%]"),
            "rhtRH3": (self.rhtRH3, "IEB rht sensor humidity [%]"),
            "rhtT1": (self.rhtT1, "IEB rht sensor Temperature [C]"),
            "rhtT2": (self.rhtT2, "IEB rht sensor Temperature [C]"),
            "rhtT3": (self.rhtT3, "IEB rht sensor Temperature [C]"),
            "rtd1": (self.rtd1, "IEB rtd sensor Temperature [C]"),
            "rtd2": (self.rtd2, "IEB rtd sensor Temperature [C]"),
            "rtd3": (self.rtd3, "IEB rtd sensor Temperature [C]"),
            "rtd4": (self.rtd4, "IEB rtd sensor Temperature [C]"),
            "LN2NIR": (
                self.ln2nir,
                "Cryogenic solenoid valve power of NIR camera for LN2",
            ),
            "LN2RED": (
                self.ln2red,
                "Cryogenic solenoid valve power of RED camera for LN2",
            ),
            "HARTMANN": (f"{left} {right}", "Left/right. 0=open 1=closed"),
            "RPRESS": (
                self.r1_pressure,
                "Pressure from the transducer of r1 cryostat",
            ),
            "BPRESS": (
                self.b1_pressure,
                "Pressure from the transducer of b1 cryostat",
            ),
            "ZPRESS": (
                self.z1_pressure,
                "Pressure from the transducer of z1 cryostat",
            ),
            self.testccd: {
                "DEPTHA": self.gage_A,
                "DEPTHB": self.gage_B,
                "DEPTHC": self.gage_C,
            },
            "LABTEMP": (self.labtemp, "Govee H5179 lab temperature [C]"),
            "IMAGETYP": (flavour, "Image type"),
        }

        log.debug(f"{pretty(datetime.datetime.now())} | check_lamp: {check_lamp}")

        # error report from Pavan & Nick 20220309
        if check_lamp is not False:
            print(check_lamp)
            header_dict.update(check_lamp)
        elif check_lamp is False:
            print(check_lamp)
            check_lamp = {
                "ARGON": self.argon,
                "XENON": self.xenon,
                "HGAR": self.hgar,
                "LDLS": self.ldls,
                "KRYPTON": self.krypton,
                "NEON": self.neon,
                "HGNE": self.hgne,
                "NIRLED": self.nirled,
            }

        log.debug(f"{pretty(datetime.datetime.now())} | header_dict: {header_dict}")

        # adding header to here 20211222 CK

        extra_header = json.loads(header)
        if header:
            header_dict.update(extra_header)

        header_json = json.dumps(header_dict, indent=None)

        return header_json

    async def read_govee(self, command):

        # Check the status of govee from lvmieb
        govee_status_cmd = await command.actor.send_command("lvmieb", "labtemp")
        await govee_status_cmd

        if govee_status_cmd.status.did_fail:
            command.info(text="Failed to receive the status of the govee (lab) sensor")
        else:
            replies = govee_status_cmd.replies
            self.labtemp = replies[-2].body["labtemp"]
            self.labhum = replies[-2].body["labhum"]

        return self.labtemp, self.labhum


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


def convert(flag: bool):
    if flag:
        return "ON"
    else:
        return "OFF"


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
