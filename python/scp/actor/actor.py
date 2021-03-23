#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong YANG (mingyeong@khu.ac.kr)
# @Date: 2021-03-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import annotations

import asyncio
import os
import warnings
from contextlib import suppress

from clu.actor import AMQPActor

__all__ = ["SCP_Actor"]

class SCP_Actor(AMQPActor):
    """SCP controller actor.
    In addition to the normal arguments and keyword parameters for
    `~clu.actor.AMQPActor`, the class accepts the following parameters.
    Parameters
    ----------
    controllers
        The list of `.SCP_Controller` instances to manage.
    """

    #parser = SCP_command_parser

    def __init__(
        self,
        *args,
        controllers: tuple[SCP_Controller, ...] = (),
        **kwargs,
    ):
        #: dict[str, SCP_Controller]: A mapping of controller name to controller.
        self.controllers = {c.name: c for c in controllers}

        self.parser_args = [self.controllers]

"""
        if "schema" not in kwargs:
            kwargs["schema"] = os.path.join(
                os.path.dirname(__file__),
                "../etc/SCP.json",
            )
"""
        super().__init__(*args, **kwargs)

        self.observatory = os.environ.get("OBSERVATORY", "LCO")
        self.version = "0.1.0"

        self.name = "scp_actor"
        self.user = "guest"
        self.password = "guest"
        self.host = "localhost"
        self.port = 5672

