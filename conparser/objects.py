# -*- coding: utf-8 -*-
import csv
import collections
import re

import chardet

import conparser.const as const
import conparser.exception as exception
import conparser.utils as utils

__author__ = "NeveHanter <nevehanter@gmail.com>"


class Object(object):
    """
    Main abstract object
    """
    def __init__(self, raw, strict):
        if isinstance(raw, list):
            self.raw = raw
        else:
            raise TypeError

        self.reencode()

        self.strict = strict

        self.data = None
        self.filled = False
        self.valid = False

        self.type = None

    def reencode(self):
        """ Detects encoding using chardet package and reencode all data to utf-8 """
        encoding = chardet.detect("".join(self.raw))
        self.raw = [line.decode(encoding['encoding']).encode('utf-8') for line in self.raw]

    def fill_object(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    @property
    def length(self):
        raise NotImplementedError

    def is_valid(self, _type):
        return self.type and self.type.upper() == _type.upper()


class CSV(Object):
    """
    Comma Separated Values
    """
    def __init__(self, raw, strict):
        super(CSV, self).__init__(raw, strict)

        self.type = const.TYPE_CSV
        self.columns = []

        self.fill_object()

    def fill_object(self):
        data = []

        for delimiter in const.CSV_DELIMITERS:
            reader = csv.reader(self.raw, delimiter=delimiter)
            for row in reader:
                print(", ".join(row))

        self.data = data
        self.filled = True

    def validate(self):
        self.valid = False

    @property
    def length(self):
        return 0


class VCardParameter(object):
    def __init__(self, name, value):
        self.name = name
        self.value = value

    @property
    def data(self):
        return dict(name=self.name, value=self.value)


class VCardTag(object):
    def __init__(self, group, name, params, value):
        self.group = group
        self.name = name
        self.params = params or ""
        self.value = value

    def get_value(self):
        return self.value

    def get_params(self):
        if not self.params:
            return []

        param_regexpr = "^(.+)=(.*)$"

        params = []
        for param in self.params.split(';'):
            param_groups = re.search(param_regexpr, param).groups()
            params.append(VCardParameter(param_groups[0], param_groups[1]))
        return params

    def get_param(self, name):
        name = name.upper()

        params = self.get_params()
        for param in params:
            if param.name == name:
                return param

        raise exception.NotFoundError("Parameter {} of tag {} not found".format(name, self.name))


class VCardEntry(object):
    def __init__(self):
        self.values = collections.OrderedDict()
        self.groups = collections.OrderedDict()

    def add(self, tag):
        """ Add tag to vCard entry """
        if tag.group:
            if tag.group in self.groups:
                if tag.name in self.groups[tag.group]:
                    self.groups[tag.group][tag.name].append(tag)
                else:
                    self.groups[tag.group] = {tag.name: [tag]}
            else:
                self.groups[tag.group] = {tag.name: [tag]}

        if tag.name in self.values:
            self.values[tag.name].append(tag)
        else:
            self.values[tag.name] = [tag]

    def get(self, name=None, group_name=None):
        """ Get tags with given name from vCard entry """
        if not name:
            return self.values

        name = name.upper()

        if not group_name:
            tag = self.values.get(name)
            if tag:
                return tag

            for key, group in self.groups.iteritems():
                if tag in group:
                    raise exception.NotFoundButFoundInGroupError("Tag {} found in group {}".format(name, key))

            raise exception.NotFoundError("Tag {} not found".format(name))
        else:
            group = self.groups.get(group_name)
            if group:
                if name in group:
                    return group[name]
                else:
                    raise exception.NotFoundError("Tag {} not found in group {}".format(name, group_name))

            raise exception.NotFoundError("Group {} not found".format(group_name))

    def get_single(self, name, group_name=None):
        """ Returns first found tag with given name """
        return self.get(name, group_name)[0]

    def get_tag_indexes(self, name):
        """ Get all indexes of tag with given name """
        name = name.upper()

        ids = []
        for index, item in enumerate(self.values.iteritems()):
            if item[0] == name:  # item[0] == key
                ids.append(index)

        if ids:
            return ids

        raise exception.NotFoundError("Tag {} not found".format(name))

    def get_tag_index(self, name):
        """ Get all indexes of tag with given name """
        return self.get_tag_indexes(name)[0]

    def count_tag(self, name):
        """ Tells how many entries with given name is in tag """
        return len(self.get_tag_indexes(name))

    def has_tag(self, name):
        """ Tells if entry contains at least one tag with given name """
        name = name.upper()

        return name in self.values


class VCard(Object):
    """
    Main vCard object
    """
    def __init__(self, raw, strict):
        super(VCard, self).__init__(raw, strict)

        self.type = utils.detect_vcard_type(self)
        self.version = utils.detect_vcard_version(self)

        self.validate()

    def fill_object(self):
        """ Parses raw data and fills internal vCard representation """
        data = []

        # 0 - group (optional), 1 - tag, 2 - params (optional), 3 - value
        line_regexpr = "^(?:([\w\d-]*)\.)?([\w\d-]+)(?:;(.*))?:(.*)$"

        entry = VCardEntry()
        for line in self.raw:
            groups = re.search(line_regexpr, line).groups()

            entry.add(
                VCardTag(
                    group=groups[0],
                    name=groups[1].upper(),
                    params=groups[2],
                    value=groups[3].replace('\r', '').replace('\n', '')
                )
            )

            if groups[1].upper() == "END":
                # We've found next entry, so we push actual and begin creating new
                data.append(entry)
                entry = VCardEntry()

        self.data = data
        self.filled = True

    @property
    def standard_tags(self):
        return const.VCARD_STANDARD_TAGS_MAP[self.version]

    @property
    def required_tags(self):
        return const.VCARD_REQUIRED_TAGS_MAP[self.version]

    def validate(self):
        """ Validates vCard object data """
        # Count every BEGIN and END tags, they should equal
        if not len(self.get_entries_with_tag("BEGIN")) == len(self.get_entries_with_tag("END")):
            raise exception.VCardValidationError("Unmatched BEGIN/END tags")

        # Check if each entry contains required tags and it's tags are well defined in accepted ones
        if self.strict:
            for entry in self.get_entries():
                if not all([entry.has_tag(tag) for tag in self.required_tags]):
                    raise exception.VCardValidationError("vCard does not contains required tags")

                for tag in entry.values:
                    if tag in self.standard_tags:
                        continue
                    if re.match(const.VCARD_X_TAG, tag):
                        continue
                    raise exception.VCardValidationError("vCard contains unknown tag {}".format(tag))

        # Checks for vCard 4.0
        if self.version == const.VCARD_VERSION_4_0:
            # Check if in every parameter VERSION tag is placed immediately after BEGIN
            for parameter in self.data:
                if parameter.get_tag_index("BEGIN") != parameter.get_tag_index("VERSION") - 1:
                    raise exception.VCardValidationError("VERSION tag should be placed immediately after BEGIN tag")

        self.valid = True

    def get_entries_with_tag(self, name, with_groups=False):
        """ Returns all entries which contains given tag
        :param name: tag to find
        :return: tags which contains given tag
        """
        entries = []
        for entry in self.data:
            try:
                entry.get(name)
                entries.append(entry)
            except exception.NotFoundButFoundInGroupError:
                if with_groups:
                    entries.append(entry)
            except exception.NotFoundError:
                continue

        return entries

    def get_entries(self):
        return self.data

    @property
    def length(self):
        return len(self.get_entries_with_tag("BEGIN"))