# !usr/bin/env python
# -*- coding: utf-8 -*-
#
# Licensed under a 3-clause BSD license.
#
# @Author: Brian Cherinka
# @Date:   2017-12-05 12:01:21
# @Last modified by:   Brian Cherinka
# @Last Modified time: 2017-12-05 12:19:32

from __future__ import absolute_import, division, print_function


class lvmscpError(Exception):
    """A custom core lvmscp exception"""

    def __init__(self, message=None):

        message = "There has been an error" if not message else message

        super(lvmscpError, self).__init__(message)


class lvmscpNotImplemented(lvmscpError):
    """A custom exception for not yet implemented features."""

    def __init__(self, message=None):

        message = "This feature is not implemented yet." if not message else message

        super(lvmscpNotImplemented, self).__init__(message)


class lvmscpAPIError(lvmscpError):
    """A custom exception for API errors"""

    def __init__(self, message=None):
        if not message:
            message = "Error with Http Response from lvmscp API"
        else:
            message = "Http response error from lvmscp API. {0}".format(message)

        super(lvmscpAPIError, self).__init__(message)


class lvmscpApiAuthError(lvmscpAPIError):
    """A custom exception for API authentication errors"""

    pass


class lvmscpMissingDependency(lvmscpError):
    """A custom exception for missing dependencies."""

    pass


class lvmscpWarning(Warning):
    """Base warning for lvmscp."""


class lvmscpUserWarning(UserWarning, lvmscpWarning):
    """The primary warning class."""

    pass


class lvmscpSkippedTestWarning(lvmscpUserWarning):
    """A warning for when a test is skipped."""

    pass


class lvmscpDeprecationWarning(lvmscpUserWarning):
    """A warning for deprecated features."""

    pass
