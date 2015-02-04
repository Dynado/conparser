# -*- coding: utf-8 -*-
__author__ = "NeveHanter <nevehanter@gmail.com>"


class Error(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class NotFoundError(Error):
    """ Base not found error """
    def __init__(self, msg):
        super(NotFoundError, self).__init__(msg)


class NotFoundTagError(NotFoundError):
    """ Raised when given tag was not found """
    def __init__(self, msg):
        super(NotFoundTagError, self).__init__(msg)


class NotFoundGroupError(NotFoundError):
    """ Raised when given group was not found """
    def __init__(self, msg):
        super(NotFoundGroupError, self).__init__(msg)


class NotFoundButFoundInGroupError(NotFoundError):
    """ Raised when given tag was not found in global parameter but found in it's groups """
    def __init__(self, msg):
        super(NotFoundButFoundInGroupError, self).__init__(msg)


class VCardVersionError(Error):
    """ Base not found error """
    def __init__(self, msg):
        super(VCardVersionError, self).__init__(msg)


class CannotDetermineVCardVersionError(VCardVersionError):
    """ Raised when vCard version detection fails """
    def __init__(self, msg):
        super(CannotDetermineVCardVersionError, self).__init__(msg)


class UnknownVCardVersionError(VCardVersionError):
    """ Raised when vCard version detection finds unknown version """
    def __init__(self, msg):
        super(UnknownVCardVersionError, self).__init__(msg)


class VCardValidationError(Error):
    """ Raised when vCard validation fails """
    def __init__(self, msg):
        super(VCardValidationError, self).__init__(msg)