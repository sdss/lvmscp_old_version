import logging

from clu.command import Command

from sdsstools import get_logger

from lvmscp.actor.supervisor import Supervisor

from . import parser


# from clu.parsers.click import command_parser

# logging
log = get_logger("sdss-lvmscp")

log.sh.setLevel(logging.DEBUG)

spectro_list = ["sp1", "sp2", "sp3"]


@parser.command()
async def status(command: Command, supervisors: dict[str, Supervisor]):
    """Actor commmand that prints the status of the connected hardwares

    Args:
        command (Command): CLU AMQP command class
        supervisors (dict[str, Supervisor]): supervisor instance of spectrograph sp1, sp2, sp3

    Returns:
        [type]: command.finish(status_dict)
    """

    status_dict = {}

    for spectro in supervisors:
        if supervisors[spectro].ready:
            await supervisors[spectro].UpdateStatus(command)

    log.info("status logged successfully!")
    updateReadyDict(status_dict, supervisors)

    # command.info(status=status_dict)

    return command.finish(stat=status_dict)


@parser.command()
async def powerstat(command: Command, supervisors: dict[str, Supervisor]):
    """Actor command that updates the powerstatus from the lvmnps

    Args:
        command (Command): CLU AMQP Command class
        supervisors (dict[str, Supervisor]): supervisor class

    Returns:
        [type]: command.finish()
    """
    for spectro in supervisors:
        if supervisors[spectro].ready:
            await supervisors[spectro].UpdatePowerStatus(command)

    return command.finish()


def updateReadyDict(item: dict, supervisors):
    """Updating the dictionary of the status

    Args:
        item (dict): the target dictionary that will be updated
        supervisors ([type]): the supervisor classes that has the real-time telemetry data
        of each hardware component
    """

    for spectro in supervisors:
        if supervisors[spectro].ready:
            item.update(
                {
                    spectro: {
                        "archon": {
                            "status": supervisors[spectro].archon_status[0],
                            "r1ccdtemp": supervisors[spectro].r1ccd_temp,
                            "r1heater": supervisors[spectro].r1heater,
                            "b1ccdtemp": supervisors[spectro].b1ccd_temp,
                            "b1heater": supervisors[spectro].b1heater,
                            "z1ccdtemp": supervisors[spectro].z1ccd_temp,
                            "z1heater": supervisors[spectro].z1heater,
                        },
                        "shutter": {
                            "shutter_power_status": supervisors[
                                spectro
                            ].shutter_power_status,
                            "shutter_status": supervisors[spectro].shutter_status,
                        },
                        "hartmann": {
                            "hartmann_left_power_status": supervisors[
                                spectro
                            ].hartmann_left_power_status,
                            "hartmann_right_power_status": supervisors[
                                spectro
                            ].hartmann_right_power_status,
                            "hartmann_left_status": supervisors[
                                spectro
                            ].hartmann_left_status,
                            "hartmann_right_status": supervisors[
                                spectro
                            ].hartmann_right_status,
                        },
                        "ieb": {
                            "humidity": {
                                "rhtRH1": supervisors[spectro].rhtRH1,
                                "rhtRH2": supervisors[spectro].rhtRH2,
                                "rhtRH3": supervisors[spectro].rhtRH3,
                            },
                            "temperature": {
                                "rhtT1": supervisors[spectro].rhtT1,
                                "rhtT2": supervisors[spectro].rhtT2,
                                "rhtT3": supervisors[spectro].rhtT3,
                                "rtd1": supervisors[spectro].rtd1,
                                "rtd2": supervisors[spectro].rtd2,
                                "rtd3": supervisors[spectro].rtd3,
                                "rtd4": supervisors[spectro].rtd4,
                            },
                        },
                        "transducer": {
                            "temperature": {
                                "r1": supervisors[spectro].r1_temperature,
                                "b1": supervisors[spectro].b1_temperature,
                                "z1": supervisors[spectro].z1_temperature,
                            },
                            "pressure": {
                                "r1": supervisors[spectro].r1_pressure,
                                "b1": supervisors[spectro].b1_pressure,
                                "z1": supervisors[spectro].z1_pressure,
                            },
                        },
                        "testccd": supervisors[spectro].testccd,
                        "lineargage": {
                            supervisors[spectro].testccd: {
                                "a": supervisors[spectro].gage_A,
                                "b": supervisors[spectro].gage_B,
                                "c": supervisors[spectro].gage_C,
                            }
                        },
                        "labtemp": supervisors[spectro].labtemp,
                        "labhumidity": supervisors[spectro].labhum,
                    }
                }
            )

    return


def convert(flag: bool):
    if flag:
        return "ON"
    else:
        return "OFF"


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
