# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import print_function, division, absolute_import


class SCPError(Exception):
    """A custom core SCP exception"""

    def __init__(self, message=None):

        message = 'There has been an error' \
            if not message else message

        super(SCPError, self).__init__(message)


class SCPNotImplemented(SCPError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = 'This feature is not implemented yet.' \
            if not message else message

        super(SCPNotImplemented, self).__init__(message)


class SCPAPIError(SCPError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = 'Error with Http Response from SCP API'
        else:
            message = 'Http response error from SCP API. {0}'.format(message)

        super(SCPAPIError, self).__init__(message)


class SCPApiAuthError(SCPAPIError):
    """A custom exception for API authentication errors"""
    pass


class SCPMissingDependency(SCPError):
    """A custom exception for missing dependencies."""
    pass


class SCPWarning(Warning):
    """Base warning for SCP."""


class SCPUserWarning(UserWarning, SCPWarning):
    """The primary warning class."""
    pass


class SCPSkippedTestWarning(SCPUserWarning):
    """A warning for when a test is skipped."""
    pass


class SCPDeprecationWarning(SCPUserWarning):
    """A warning for deprecated features."""
    pass
