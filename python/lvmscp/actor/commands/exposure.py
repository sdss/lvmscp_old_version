#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong YANG (mingyeong@khu.ac.kr)
# @Date: 2021-03-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

import asyncio

import click

from lvmscp.exceptions import lvmscpError

from . import parser


# lock for exposure lock
exposure_lock = asyncio.Lock()


@parser.command()
@click.argument("COUNT", type=int, default=1, required=False)
@click.argument(
    "FLAVOUR",
    type=click.Choice(["bias", "object", "flat", "dark"]),
    default="object",
    required=False,
)
@click.argument("EXPTIME", type=float)
async def exposure(command, exptime: float, count: int, flavour: str):
    """Exposes the camera."""

    # lock for exposure sequence only running for once
    async with exposure_lock:
        # Check the actor is running
        try:
            lvmieb_status_cmd = await command.actor.send_command("lvmieb", "ping")
            await lvmieb_status_cmd
        except lvmscpError as err:
            return command.fail(error=str(err))

        if lvmieb_status_cmd.status.did_fail:
            return command.fail(text=lvmieb_status_cmd.status)

        # Check the actor is running
        try:
            lvmnps_status_cmd = await command.actor.send_command("lvmnps", "ping")
            await lvmnps_status_cmd
        except lvmscpError as err:
            return command.fail(error=str(err))

        if lvmnps_status_cmd.status.did_fail:
            return command.fail(text=lvmnps_status_cmd.status)

        # Check the actor is running
        try:
            archon_status_cmd = await command.actor.send_command("archon", "ping")
            await archon_status_cmd
        except lvmscpError as err:
            return command.fail(error=str(err))

        if archon_status_cmd.status.did_fail:
            return command.fail(text=archon_status_cmd.status)

        if flavour != "bias" and exptime is None:
            raise click.UsageError("EXPOSURE-TIME is required unless --flavour=bias.")
        elif flavour == "bias":
            exptime = 0.0

        if exptime < 0.0:
            raise click.UsageError("EXPOSURE-TIME cannot be negative")

        # check the power of the shutter & hartmann doors
        wago_power_status_cmd = await command.actor.send_command(
            "lvmieb", "wago getpower"
        )
        await wago_power_status_cmd

        if wago_power_status_cmd.status.did_fail:
            return command.fail(
                text="Failed to receive the power status from wago relays"
            )

        replies = wago_power_status_cmd.replies
        shutter_power_status = replies[-1].body["shutter_power"]
        hartmann_left_power_status = replies[-1].body["hartmann_left_power"]
        hartmann_right_power_status = replies[-1].body["hartmann_right_power"]

        if shutter_power_status == "OFF":
            return command.fail(
                text="Cannot start exposure : Exposure shutter power off"
            )
        elif hartmann_left_power_status == "OFF":
            return command.fail(
                text="Cannot start exposure : Left hartmann door power off"
            )
        elif hartmann_right_power_status == "OFF":
            return command.fail(
                text="Cannot start exposure : Right hartmann door power off"
            )

        # Check the status (opened / closed) of the shutter
        shutter_status_cmd = await command.actor.send_command(
            "lvmieb", "shutter status"
        )
        await shutter_status_cmd

        if shutter_status_cmd.status.did_fail:
            return command.fail(
                text="Failed to receive the status of the shutter status"
            )

        replies = shutter_status_cmd.replies
        shutter_status_before = replies[-1].body["shutter"]

        if shutter_status_before != "closed":
            return command.fail(text="Shutter is already opened. The command will fail")

        # Check the status (opened / closed) of the hartmann doors
        hartmann_status_cmd = await command.actor.send_command(
            "lvmieb", "hartmann status"
        )
        await hartmann_status_cmd

        if hartmann_status_cmd.status.did_fail:
            return command.fail(
                text="Failed to receive the status of the hartmann status"
            )

        replies = hartmann_status_cmd.replies
        hartmann_left_status = replies[-1].body["hartmann_left"]
        hartmann_right_status = replies[-1].body["hartmann_right"]

        if flavour == "object" or flavour == "flat":
            if not (
                hartmann_left_status == "opened" and hartmann_right_status == "opened"
            ):
                return command.fail(
                    text="Hartmann doors are not opened for the science exposure"
                )

        # Check that the configuration has been loaded.
        archon_cmd = await (await command.actor.send_command("archon", "status"))
        if archon_cmd.status.did_fail:
            command.fail(text="Failed getting status from the controller")

        replies = archon_cmd.replies
        check_idle = replies[-2].body["status"]["status_names"][0]
        if check_idle != "IDLE":
            return command.fail(text="archon is not initialized")

        command.info(text="Starting the exposure.")

        # Turn on the flat lamp for flat sequence, have to check the lamp is already on..
        if flavour == "flat":
            flat_lamp_cmd = await (
                await command.actor.send_command("lvmnps", 'on "625 nm LED (M625L4)"')
            )
            if flat_lamp_cmd.status.did_fail:
                command.fail(text="Failed getting status from the network power switch")
            replies = flat_lamp_cmd.replies
            check_lamp = replies[-2].body["STATUS"]["DLI-NPS-01"][
                "625 nm LED (M625L4)"
            ]["STATE"]
            if check_lamp:
                command.info(text="flat lamp is on!")
            else:
                return command.fail(text="flat lamp is off...")

        # start exposure loop
        for nn in range(count):

            command.info(f"Taking exposure {nn + 1} of {count}.")

            # Read pressure.
            # pressure = await send_message("@253P?\\")
            # command.info(pres = pressure)

            # Build extra header.
            # header = {"PRESSURE": (pressure, "Spectrograph pressure [torr]")}
            # header_json = json.dumps(header, indent=None)
            # command.info("added header")

            # Flushing
            flush_count = 1
            if flush_count > 0:
                command.info("Flushing")
                archon_cmd = await (
                    await command.actor.send_command("archon", f"flush {flush_count}")
                )

            if archon_cmd.status.did_fail:
                return command.fail(text="Failed flushing")

            # Start exposure
            archon_cmd = await (
                await command.actor.send_command(
                    "archon",
                    f"expose start --{flavour} {exptime}",
                )
            )
            if archon_cmd.status.did_fail:
                await command.actor.send_command("archon", "expose abort --flush")
                return command.fail(
                    text="Failed starting exposure. Trying to abort and exiting."
                )
            else:
                reply = archon_cmd.replies
                print(reply[-2].body["text"])
                command.info(text=reply[-2].body["text"])

            if flavour != "bias" and exptime > 0:
                # Use command to access the actor and command the shutter

                command.info("Opening the shutter")

                shutter_cmd = await command.actor.send_command("lvmieb", "shutter open")
                await shutter_cmd

                if shutter_cmd.status.did_fail:
                    await command.actor.send_command("lvmieb", "shutter close")
                    await command.actor.send_command("archon", "expose abort --flush")
                    return command.fail(text="Shutter failed to open")

                # Report status of the shutter
                replies = shutter_cmd.replies
                shutter_status = replies[-1].body["shutter"]
                if shutter_status not in ["opened", "closed"]:
                    return command.fail(
                        text=f"Unknown shutter status {shutter_status!r}."
                    )

                command.info(f"Shutter is now {shutter_status!r}.")

                if not (
                    await asyncio.create_task(close_shutter_after(command, exptime))
                ):
                    await command.actor.send_command("archon", "expose abort --flush")
                    return command.fail(text="Failed to close the shutter")

            command.info(text="readout . . .")
            # Finish exposure
            archon_cmd = await (
                await command.actor.send_command(
                    "archon",
                    "expose finish",
                    # f"--header '{header_json}'",
                )
            )
            if archon_cmd.status.did_fail:
                command.fail(text="Failed reading out exposure")

            # For monitering the status
            while True:
                readout_cmd = await command.actor.send_command("archon", "status")
                await readout_cmd
                readout_replies = readout_cmd.replies
                archon_readout = readout_replies[-2].body["status"]["status_names"][0]
                if archon_readout == "READING":
                    continue
                else:
                    command.info(text="readout finished!")
                    break

            replies = archon_cmd.replies
            print(replies[-11].body)
            print(replies[-10].body)
            print(replies[-9].body)
            print(replies[-8].body)
            print(replies[-7].body)
            print(replies[-6].body)
            print(replies[-5].body)
            print(replies[-4].body)
            print(replies[-3].body)

            command.info(replies[-8].body)
            command.info(replies[-7].body)
            command.info(replies[-6].body)
            command.info(replies[-5].body)
            command.info(replies[-4].body)
            command.info(replies[-3].body)
            command.info(replies[-2].body)

        # Turn off the flat lamp for flat sequence
        if flavour == "flat":
            flat_lamp_cmd = await (
                await command.actor.send_command("lvmnps", 'off "625 nm LED (M625L4)"')
            )
            if flat_lamp_cmd.status.did_fail:
                command.fail(text="Failed getting status from the network power switch")
            replies = flat_lamp_cmd.replies
            check_lamp = replies[-2].body["STATUS"]["DLI-NPS-01"][
                "625 nm LED (M625L4)"
            ]["STATE"]
            if not check_lamp:
                command.info(text="flat lamp is off!")
            else:
                return command.fail(text="flat lamp is on...")

        return command.finish(text="Exposure sequence done!")


async def close_shutter_after(command, delay: float):
    """Waits ``delay`` before closing the shutter."""

    command.info(text="exposing . . .")
    await asyncio.sleep(delay)

    command.info(text="Closing the shutter")
    shutter_cmd = await command.actor.send_command("lvmieb", "shutter close")
    await shutter_cmd

    if shutter_cmd.status.did_fail:
        command.fail(text="Shutter failed to close.")
        return False

    replies = shutter_cmd.replies
    shutter_status = replies[-1].body["shutter"]
    if shutter_status not in ["opened", "closed"]:
        return command.fail(text=f"Unknown shutter status {shutter_status!r}.")

    command.info(text=f"Shutter is now '{shutter_status}'")
    return True
