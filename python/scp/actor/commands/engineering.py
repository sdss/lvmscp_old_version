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

    #Check that the actor is running
    """ 
    client = AMQPClient(
        "SCP",
        host= "localhost",
        port= 5672,
        models=["archon"],
    )
    await client.start()
    if len(client.models) == 0:
        command.fail(text="Archon actor does not seem to be running. Run with 'archon start'")

    model = client.models["archon"]
    """
    command.info(text="Starting the exposure.")

    # Check that the configuration has been loaded.

    cmd = await (await command.actor.send_command("archon", "status"))
    if cmd.status.did_fail:
        #log.error("Failed getting status from the controller.")
        command.fail(text="Failed getting status from the controller")
    """
    #status = await get_controller_status(client)
    if status.did_fail != True:
        #log.warning("Archon has not been initialised. Sending configuration file.")
        cmd = await (await command.actor.send_command("archon", "init"))
        if cmd.status.did_fail:
            #log.error("Failed initialising the Archon.")
            command.fail(text="Failed initialising the Archon.")
    """
    """
    # Check if the shutter responds and is closed
    shutter_check_cmd = await command.actor.send_command("OsuActor", "check")
    
    await shutter_check_cmd  # Block until the command is done (finished or failed)
    if shutter_check_cmd.status.did_fail:
        # Do cleanup
        return command.fail(text="failed to receive shutter status")
    """
    """
    # If there is a readout pending, flush the camera.
    if status & CS.READOUT_PENDING:
        log.warning("Pending readout found. Aborting and flushing.")
        if status & CS.EXPOSING:
            cmd_str = "expose abort --all --flush"
        else:
            cmd_str = "flush"
        cmd = await (await client.send_command("archon", cmd_str))
        if cmd.status.did_fail:
            log.error("Failed flushing.")
            sys.exit(1)
    """
    
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
        #log.debug("Reading pressure transducer.")
        pressure = await send_message("@253P?\\")
        command.info("pressure data received")

        # Build extra header.
        header = {"PRESSURE": (pressure, "Spectrograph pressure [torr]")}
        header_json = json.dumps(header, indent=None)
        command.info("added header")
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
                f"expose start sp1 --{flavour} {exptime}",
            )
        )
        if cmd.status.did_fail:
            #log.error("Failed starting exposure. Trying to abort and exiting.")
            await command.actor.send_command("archon", "expose abort --flush")
            command.fail(text = "Failed starting exposure. Trying to abort and exiting.")

        if flavour != "bias" and exptime > 0:
            # Use command to access the actor and command the shutter
            shutter_cmd = await command.actor.send_command("OsuActor", "open")

            await shutter_cmd  # Block until the command is done (finished or failed)
            if shutter_cmd.status.did_fail:
                await command.actor.send_command("OsuACtor", "close")
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
            
            """
            #log.debug("Opening shutter.")
            #result = await command_shutter("QX3")
            if result is False:
                log.error("Shutter failed to open.")
                await command_shutter("QX4")
                await client.send_command("archon", "expose abort --flush")
                sys.exit(1)

            if not (await asyncio.create_task(close_shutter_after(exposure_time))):
                await client.send_command("archon", "expose abort --flush")
                sys.exit(1)
            """

        # Finish exposure
        command.info("Finishing exposure and reading out.")
        
        delay_readout = 0
        if delay_readout > 0:
            command.info(f"Readout will be delayed {delay_readout} seconds.")

        cmd = await (
            await command.actor.send_command(
                "archon",
                f"expose finish --delay-readout {delay_readout} "
                f"--header '{header_json}'",
            )
        )
        if cmd.status.did_fail:
            command.fail(text="Failed reading out exposure.")

        #exp_name = model["filename"].value

    """
    #receive pressure data from the pressure transcducer
    
    pres = await send_message("@253P?\\")
    temp = await send_message("@253T?\\")
    command.info(text=f"transducer pressure : {pres!r}")
    command.info(text=f"transducer temperature: {temp!r}")

    #send archon command
    await (await command.actor.send_command("archon", f"expose start {exptime} --object"))

    # Use command to access the actor and command the shutter
    shutter_cmd = await command.actor.send_command("OsuActor", "open")

    await shutter_cmd  # Block until the command is done (finished or failed)
    if shutter_cmd.status.did_fail:
        # Do cleanup
        return command.fail(text="Shutter failed to open")

    # Report status of the shutter
    replies = shutter_cmd.replies
    shutter_status = replies[-1].body["shutter"]
    if shutter_status not in ["open", "closed"]:
        return command.fail(text=f"Unknown shutter status {shutter_status!r}.")

    command.info(f"Shutter is now {shutter_status!r}.")

    # Sleep until the exposure is complete.
    command.info(text="exposing by archon...")
    await asyncio.sleep(exptime)

    # Close the shutter. Note the double await.
    await (await command.actor.send_command("OsuActor", "close"))

    await (await command.actor.send_command("archon", "expose finish"))

    # Add fits header



    # Finish exposure, read buffer, etc.
    """


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

    await asyncio.sleep(delay)

    #log.debug("Closing shutter")

    result = await command.actor.send_command("OsuActor", "close")
    if result is False:
        command.fail(text="Shutter failed to close.")
        return False

    return True
