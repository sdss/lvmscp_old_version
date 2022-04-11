# /usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong YANG (mingyeong@khu.ac.kr)
# @Date: 2021-03-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import absolute_import, annotations, division, print_function

import os
from typing import ClassVar, Dict

from clu.actor import AMQPActor

from lvmscp.actor.supervisor import Supervisor

from .commands import parser as SCP_command_parser


# from scpactor import __version__

__all__ = ["lvmscp"]

spectro_list = ["sp1", "sp2", "sp3"]


class lvmscp(AMQPActor):
    """the main actor class of the lvmscp. Based on the AMQPActor from clu.actor

    Args:
        AMQPActor ([type]): class of the base actor from clu.actor
    """

    parser = SCP_command_parser
    BASE_CONFIG: ClassVar[str | Dict | None] = None

    def __init__(
        self,
        *args,
        supervisors: tuple[Supervisor, ...] = (),
        **kwargs,
    ):
        if "schema" not in kwargs:
            kwargs["schema"] = os.path.join(
                os.path.dirname(__file__),
                "../etc/schema.json",
            )
        super().__init__(*args, **kwargs)
        self.supervisors = {s.name: s for s in supervisors}

    async def start(self):
        """Start the actor and connect the controllers."""
        await super().start()
        # add code for pinging lower actors by cluplus (CK 20220226)

    async def stop(self):
        return await super().stop()

    @classmethod
    def from_config(cls, config, *args, **kwargs):
        """Creates an actor from a configuration file."""

        if config is None:
            if cls.BASE_CONFIG is None:
                raise RuntimeError("The class does not have a base configuration.")
            config = cls.BASE_CONFIG

        instance = super(lvmscp, cls).from_config(config, *args, **kwargs)
        assert isinstance(instance, lvmscp)
        assert isinstance(instance.config, dict)
        instance.parser_args = [instance.supervisors]
        for (ctrname, ctr) in instance.config.items():
            if ctrname in spectro_list:
                # print(ctrname, ctr)
                instance.supervisors.update({ctrname: Supervisor(ctrname)})

        # print(instance.supervisors)

        return instance
