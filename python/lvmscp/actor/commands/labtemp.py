from clu.command import Command

from lvmscp.actor.supervisor import Supervisor

from . import parser


@parser.command()
async def labtemp(command: Command, supervisors: dict[str, Supervisor]):
    """

    Args:


    Returns:
        [type]: command.finish()
    """

    for spectro in supervisors:
        if supervisors[spectro].ready:
            temp, hum = await supervisors[spectro].read_govee(command)

    command.info(f"temp is {temp}, hum is {hum}")
    return command.finish()
