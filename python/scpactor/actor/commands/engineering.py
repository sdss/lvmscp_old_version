#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong YANG (mingyeong@khu.ac.kr)
# @Date: 2021-03-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio
import click
import json

from . import parser
from clu.client import AMQPClient

@parser.command()
@click.option(
    "-c",
    "--count",
    type=int,
    default=1,
    help="Number of frames to take with this configuration.",
)
@click.option(
    "--flavour",
    "-f",
    type=str,
    default="object",
    help="object, dark, or bias.",
)
@click.argument("EXPTIME", type=float)
async def engineering(command, exptime: float, count: int, flavour: str):
    """Exposes the camera."""

    if flavour != "bias" and exptime is None:
        raise click.UsageError("EXPOSURE-TIME is required unless --flavour=bias.")
    elif flavour == "bias":
        exposure_time = 0.0

    command.info(text="Starting the exposure.")

    # Check that the configuration has been loaded.

    cmd = await (await command.actor.send_command("archon", "status"))
    if cmd.status.did_fail:
        command.fail(text="Failed getting status from the controller")

    """
    #Check the power of the devices
    command.info(text="power checking...")
    power_cmd = await command.actor.send_command("NpsActor", "status")
    await power_cmd  # Block until the command is done (finished or failed)
    if power_cmd.status.did_fail:
        # Do cleanup
        return command.fail(text="failed to check the NPS")
    command.info(text="power OK") 
    """
    #start exposure loop
    for nn in range(count):

        command.info(f"Taking exposure {nn + 1} of {count}.")

        # Read pressure.
        pressure = await send_message("@253P?\\")
        #command.info(pres = pressure)

        # Build extra header.
        header = {"PRESSURE": (pressure, "Spectrograph pressure [torr]")}
        header_json = json.dumps(header, indent=None)
        #command.info("added header")

        # Flushing
        flush_count = 1
        if flush_count > 0:
            command.info("Flushing")
            cmd = await (await command.actor.send_command("archon", f"flush {flush_count}"))

        # Start exposure.
        command.info("Starting exposure.")
        cmd = await (
            await command.actor.send_command(
                "archon",
                f"expose start --{flavour} {exptime}",
            )
        )
        if cmd.status.did_fail:
            await command.actor.send_command("archon", "expose abort --flush")
            command.fail(text = "Failed starting exposure. Trying to abort and exiting.")

        if flavour != "bias" and exptime > 0:
            # Use command to access the actor and command the shutter
            shutter_cmd = await command.actor.send_command("osuactor", "shutter open")

            await shutter_cmd  # Block until the command is done (finished or failed)
            if shutter_cmd.status.did_fail:
                await command.actor.send_command("osuactor", "shutter close")
                await command.actor.send_command("archon", "expose abort --flush")
                return command.fail(text="Shutter failed to open")
            
            # Report status of the shutter
            replies = shutter_cmd.replies
            shutter_status = replies[-1].body["shutter"]
            if shutter_status not in ["open", "closed"]:
                return command.fail(text=f"Unknown shutter status {shutter_status!r}.")

            command.info(f"Shutter is now {shutter_status!r}.")

            if not (await asyncio.create_task(close_shutter_after(command, exptime))):
                await command.actor.send_command("archon", "expose abort --flush")
                command.fail(text = "Failed to close the shutter")
    
        # Finish exposure
        cmd = await (
            await command.actor.send_command(
            "archon",
            f"expose finish",
            f"--header '{header_json}'",
            )
        )
        if cmd.status.did_fail:
            command.fail(text=f"Failed reading out exposure")
    return command.finish(text="Engineering sequence done!")

async def send_message(message):
    reader, writer = await asyncio.open_connection(
        '10.7.45.30', 1112)

    sclStr = message.upper()
    #print(f'Send: {message!r}')
    writer.write(sclStr.encode())
    await writer.drain()

    Reply = await receive_status(reader)
    fin = len(Reply)-1
    #print('reply : ', Reply)
    #print('Close the connection')
    writer.close()
    await writer.wait_closed()

    return Reply[7:fin]

async def receive_status(areader):
    sclReply = ""
    data = await areader.read(4096)
    recStr = data.decode()
    return recStr

async def close_shutter_after(command, delay: float):
    """Waits ``delay`` before closing the shutter."""

    command.info(text = "exposing . . .")
    await asyncio.sleep(delay)


    result = await command.actor.send_command("osuactor", "shutter close")
    if result is False:
        command.fail(text="Shutter failed to close.")
        return False
    command.info(text=f"shutter is now closed")
    return True
