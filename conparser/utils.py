# -*- coding: utf-8 -*-
import re

import conparser.const as const
import conparser.exception as exception

__author__ = "NeveHanter <nevehanter@gmail.com>"


def get_object(raw, strict=True):
    """
    Creates & returns parsing object from given data
    :param raw: raw file data, list or iterable
    :param strict: enables strict validation
    :return: object
    """
    from objects import VCard, CSV

    assert raw

    if not isinstance(raw, list):
        raw = [line for line in raw]

    # Check for vCard
    if re.match("BEGIN:VCARD", raw[0]):
        return VCard(raw, strict)
    else:
        # For now we fallback to CSV
        return CSV(raw, strict)


def detect_vcard_version(vcard_object):
    """
    Detects vcard version for given object

    :param vcard_object: instance for which we check version
    :type vcard_object: VCard
    :return: found version
    :rtype: basestring

    :raises UnknownVCardVersionError, CannotDetermineVCardVersionError
    """
    from objects import VCard

    if not isinstance(vcard_object, VCard):
        raise TypeError

    if not vcard_object.filled:
        vcard_object.fill_object()

    entries = vcard_object.get_entries_with_tag("VERSION")
    if entries:
        version = entries[0].get_single("VERSION").value
        if version == "2.1":
            return const.VCARD_VERSION_2_1
        elif version == "3.0":
            return const.VCARD_VERSION_3_0
        elif version == "4.0":
            return const.VCARD_VERSION_4_0
        else:
            raise exception.UnknownVCardVersionError("Unknown version found {}".format(version))

    raise exception.CannotDetermineVCardVersionError("Cannot determne vCard version")


def detect_vcard_type(vcard_object):
    """
    Detects vcard file type for given object

    :param vcard_object: instance for which we check type
    :type vcard_object: VCard
    :return: detected type
    :rtype: basestring
    """
    from objects import VCard

    if not isinstance(vcard_object, VCard):
        raise TypeError

    return const.TYPE_VCARD