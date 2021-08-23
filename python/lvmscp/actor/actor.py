# /usr/bin/env python
# -*- coding: utf-8 -*-
#
# @Author: Mingyeong YANG (mingyeong@khu.ac.kr)
# @Date: 2021-03-22
# @Filename: actor.py
# @License: BSD 3-clause (http://www.opensource.org/licenses/BSD-3-Clause)

from __future__ import absolute_import, annotations, division, print_function

from clu.actor import AMQPActor

from .commands import parser as SCP_command_parser


# from scpactor import __version__

__all__ = ["lvmscp"]


class lvmscp(AMQPActor):
    """lvmscp controller actor.
    In addition to the normal arguments and keyword parameters for
    `~clu.actor.AMQPActor`, the class accepts the following parameters.
    Parameters
    ----------
    """

    parser = SCP_command_parser

    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
