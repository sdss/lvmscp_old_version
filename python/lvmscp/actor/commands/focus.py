import click

#  import asyncio
from . import parser


@parser.command()
@click.argument("COUNT", type=int, default=1, required=False)
@click.argument("EXPTIME", type=float, required=False)
@click.argument(
    "spectro",
    type=click.Choice(["sp1", "sp2", "sp3"]),
    default="sp1",
    required=False,
)
async def focus(command, exptime: float, count: int, spectro: str):
    """Exposure command controlling all lower actors"""

    # Turn on the lamp
    # wait for 60 seconds

    # Loop for counts

    #   set the hartmann door - left
    #   Take the flat image
    #   take the dark image
    #   take the bias image

    #   set the hartmann door - right
    #   Take the flat image
    #   take the dark image
    #   take the bias image

    # information of the saved files
