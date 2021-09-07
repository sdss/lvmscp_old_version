import click

from . import parser


@parser.group()
def hartmann(*args):
    """control the hartmann door."""

    pass


@hartmann.command()
@click.argument(
    "request",
    type=click.Choice(["right", "left", "both", "close"]),
    required=True,
)
@click.argument(
    "spectro",
    type=click.Choice(["sp1", "sp2", "sp3"]),
    default="sp1",
    required=False,
)
async def set(command, request: str, spectro: str):

    hartmann_status_cmd = await command.actor.send_command(
        "lvmieb", f"hartmann status {spectro}"
    )
    await hartmann_status_cmd

    if hartmann_status_cmd.status.did_fail:
        return "Failed to receive the status of the hartmann status"
    else:
        replies = hartmann_status_cmd.replies
        hartmann_left_status = replies[-1].body["hartmann_left"]
        hartmann_right_status = replies[-1].body["hartmann_right"]

    # Makes the status only the right door opened
    if request == "right":
        if hartmann_right_status == "closed":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann open {spectro} --side={request}"
            )
            await open_cmd
        elif hartmann_right_status == "opened":
            command.info(text=f"{request} already opened")

        if hartmann_left_status == "opened":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann close {spectro} --side=left"
            )
            await open_cmd
    elif request == "left":
        if hartmann_left_status == "closed":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann open {spectro} --side={request}"
            )
            await open_cmd
        elif hartmann_left_status == "opened":
            command.info(text=f"{request} already opened")

        if hartmann_right_status == "opened":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann close {spectro} --side=right"
            )
            await open_cmd
    elif request == "both":
        if hartmann_right_status == "closed":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann open {spectro} --side=right"
            )
            await open_cmd
        elif hartmann_right_status == "opened":
            command.info(text="right already opened")

        if hartmann_left_status == "closed":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann open {spectro} --side=left"
            )
            await open_cmd
        elif hartmann_left_status == "opened":
            command.info(text="left already opened")
    elif request == "close":
        if hartmann_right_status == "closed":
            command.info(text="right already closed")
        elif hartmann_right_status == "opened":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann close {spectro} --side=right"
            )
            await open_cmd

        if hartmann_left_status == "closed":
            command.info(text="left already closed")
        elif hartmann_left_status == "opened":
            open_cmd = await command.actor.send_command(
                "lvmieb", f"hartmann close {spectro} --side=left"
            )
            await open_cmd

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

    command.info(
        HARTMANN={
            "hartmann_left": hartmann_left_status,
            "hartmann_right": hartmann_right_status,
        }
    )
