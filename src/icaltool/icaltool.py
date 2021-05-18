#!/usr/bin/env python3
import csv
import logging
import logging.config
import re
import argparse
import pathlib
import sys

from .log import log
from . import datatypes

logger = logging.getLogger(__name__)

default_column_mapping = {
    'DTSTART': 0,
    'DTEND': 1,
    'DTSTAMP': 2,
    'UID': 3,
    'CREATED': 4,
    'DESCRIPTION': 5,
    'LAST-MODIFIED': 6,
    'LOCATION': 7,
    'SEQUENCE': 8,
    'SUMMARY': 9,
    'CATEGORIES': 10,
    'CLASS': 11,
    'ATTACH': 12,
    'TRANSP': 13,
    'RRULE': 14,
    'EXDATE': 15,
    'STATUS': 16
}

custom_column_names = {
    'DTSTART': 'DTSTART',
    'DTEND': 'DTEND',
    'DTSTAMP': 'DTSTAMP',
    'UID': 'UID',
    'CREATED': 'CREATED',
    'DESCRIPTION': 'DESCRIPTION',
    'LAST-MODIFIED': 'LAST-MODIFIED',
    'LOCATION': 'LOCATION',
    'SEQUENCE': 'SEQUENCE',
    'SUMMARY': 'SUMMARY',
    'CATEGORIES': 'CATEGORIES',
    'CLASS': 'CLASS',
    'ATTACH': 'ATTACH',
    'TRANSP': 'TRANSP',
    'RRULE': 'RRULE',
    'EXDATE': 'EXDATE',
    'STATUS': 'STATUS'
}

class ICalTool:
    def __init__(self):
        self._reset()

    def _reset(self):
        self.vcalendar = None

    def load(self, file_name, component='VEVENT',
        has_header=True, custom_column_names=custom_column_names,
        column_mapping=default_column_mapping,
        delimiter=',', quotechar='"'):

        if file_name[-3:] == 'csv':
            self.csv_load(file_name, component, has_header, custom_column_names,
                column_mapping, delimiter, quotechar)
        elif file_name[-3:] == 'ics':
            self.ical_load(file_name)
        else:
            logger.error('invalid file given ("{}")'.format(file_name))
            sys.exit()

    def csv_load(self, file_name, component='VEVENT',
        has_header=True, custom_column_names=custom_column_names,
        column_mapping=default_column_mapping,
        delimiter=',', quotechar='"'):

        with open(file_name, 'r', newline='', encoding='utf-8-sig') as \
            file_handle:

            logger.info('opening {}'.format(file_name))
            data = csv.reader(
                file_handle, delimiter=delimiter, quotechar=quotechar)

            if has_header:
                header = next(data)

            column_mapping = self._csv_get_column_mapping(
                default_column_mapping, has_header, header, custom_column_names)

            self.vcalendar = datatypes.VCALENDAR()
            self.vcalendar.csv_parse(component, data, column_mapping)
            logger.info('loaded {}'.format(file_name))

    def _csv_get_column_mapping(self, default_column_mapping, has_header,
        header, custom_column_names):

        if not has_header:
            # no headers to parse
            # so use default column mapping
            return default_column_mapping

        # get headers from file
        column_mapping = {}
        i = 0

        for column in header:
            column_mapping[column] = i
            i = i + 1

        if len(custom_column_names) == 0:
            return parsed_columns

        # the user provided costum columns names in a dictionary
        new_mapping = {}
        for column_name in column_mapping.keys():
            # so go through every available column
            try:
                # 1. the parsed column name exists in the user
                # provided dictionary
                new_mapping[custom_column_names[column_name]] = \
                    column_mapping[column_name]
            except KeyError:
                # 2. the name cannot be translated so copy it
                new_mapping[column_name] = \
                    column_mapping[column_name]
        return new_mapping

    def ical_load(self, file_name):
        with open(file_name, 'r', newline='', encoding='utf-8-sig') as \
            file_handle:

            logger.info('opening {}'.format(file_name))
            raw = file_handle.readlines()
            lines = []
            vcalendar = False
            # clean up
            for line in raw:
                # remove the trailing "\n"
                line = line.rstrip("\r\n")
                # do not use empty lines
                if not line == '':
                    if not vcalendar and line == 'BEGIN:VCALENDAR':
                        vcalendar = True
                        logger.debug('recording new VCALENDAR')
                    elif vcalendar:
                        if line == 'END:VCALENDAR':
                            vcalendar = False
                            logger.debug('finished recording VCALENDAR')
                        # unfold lines (folded lines begin with a single whitespace
                        # or tab)
                        elif line[0] == ' ' or line[0] == "\t":
                            # append to previous line
                            lines[len(lines) - 1] += line[1:]
                        else:
                            lines.append(line)
            self.vcalendar = datatypes.VCALENDAR()
            self.vcalendar.ical_parse(lines)
            logger.info('loaded {}'.format(file_name))

    def write(self, file_name, component):
        if file_name[-3:] == 'csv':
            self.csv_write(file_name, component)
        elif file_name[-3:] == 'ics':
            self.ical_write(file_name)
        else:
            logger.error('invalid file given ("{}")'.format(file_name))
            sys.exit()

    def csv_write(self, file_name, component='VEVENT'):
        lines = []
        # can only write components of one type
        with open(file_name, 'w') as file_handle:
            logger.info('writing to {}'.format(file_name))

            # get a list of known properties to use as column names
            class_object = getattr(datatypes, component)
            properties = []
            for prop, attributes in class_object.defined_properties.items():
                if attributes[0] == 2:
                    continue
                else:
                    properties.append(prop)

            # build header
            lines.append('"' + '","'.join(properties) + '"')

            # fill with data
            lines.extend(self.vcalendar.csv_write(component))

            file_handle.write("\r\n".join(lines))
            logger.info('finished writing to {}'.format(file_name))

    def ical_write(self, file_name):
        with open(file_name, 'w') as file_handle:
            logger.info('writing to {}'.format(file_name))
            lines = self.vcalendar.ical_write()
            for line in lines:
                text = ''
                while True:
                    text += line[:74] + "\r\n"
                    line = ' ' + line[74:]
                    if line == ' ':
                        break
                file_handle.write(text)
            logger.info('finished writing to {}'.format(file_name))

    def filter(self, rules):
        if self.vcalendar is None:
            logger.warning('cannot apply rules before calendar data has been '+
                'loaded')
            return

        # example component rule:
        #  - keep only events:
        #    COMPONENT:+VEVENT
        #  - filter out all events:
        #    COMPONENT:-VEVENT
        #  - filter out all events and alarms
        #    COMPONENT:-VEVENT,VALARM
        # example property rules:
        #  - filter out all components with a start date between 2015 and 2017:
        #    DTSTART:-2015to2017
        #  - keep only components with a start date between 2015-10 and 2017-11:
        #    DTSTART:+2015-10to2017-11
        #  - ... attended by john.doe@mail.domain:
        #    DTSTART:+2015-10to2017-11;ATTENDEE:+john.doe@mail.domain
        #  - ... but not by jane.doe@mail.domain:
        #    ...;ATTENDEE:+john.doe@mail.domain|-jane.doe@mail.domain

        raw_rules = rules.split(';')
        parsed_rules = {}
        for raw_rule in raw_rules:
            try:
                name, rule = raw_rule.split(':')
            except ValueError:
                # no ':'
                logger.warning('malformed rule {}'.format(raw_rule))
                continue
            logger.info('found rule for {}: "{}"'.format(name, rule))
            parsed_rules[name] = rule.split('|')

        try:
            component_rule = parsed_rules['COMPONENT'][0]
            logger.debug('found component rule: "{}"'.format(component_rule))

            # sanity check
            if not re.match('[+-]{1}[A-Z,]+', component_rule):
                logger.error('component filter cannot have inclusion and ' +
                    'exclusion criteria, "{}" given'.format(component_rule))
                return

            components_keep = component_rule[0] == '+'
            components = component_rule[1:].split(',')
            del parsed_rules['COMPONENT']
        except KeyError:
            # no component rule
            # create an empty list of components to remove
            components = []
            components_keep = False

        self.vcalendar.filter(components, components_keep,
            parsed_rules)

# taken from :
# https://stackoverflow.com/questions/9027028/argparse-argument-order
class CustomAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if not 'ordered_args' in namespace:
            setattr(namespace, 'ordered_args', [])
        previous = namespace.ordered_args
        previous.append((self.dest, values))
        setattr(namespace, 'ordered_args', previous)

def main():
    logging.config.dictConfig(log.config)

    parser = argparse.ArgumentParser(
        description='Tool to work with calendar data. It can read .ics ' +
            '(preferred) and .csv files. You can filter the compontents ' +
            '(events, todos, alarms, journals, freebusy-indicators) by their ' +
            'type or the value of their properties, e.g. start date ' +
            '(DTSTART) or organiser (ORGANIZER). The result can be written ' +
            'back to a file, again either .ics (preferred) or .csv.',
        epilog='')
    parser.add_argument(
        'file',
        help='the file to load, either .csv or .ics (preferred)',
        type=str)
    parser.add_argument(
        '-o',
        '--output',
        help='the file to write to, either .csv or .ics (preferred)',
        type=str,
        action=CustomAction)
    parser.add_argument(
        '-f',
        '--filter',
        help='rules to filter which component types (events, todos, alarms, ' +
            'journals, freebusy-indicators) to keep / sort out',
        type=str,
        action=CustomAction)
    parser.add_argument(
        '-c',
        '--component',
        help='component type stored in the .csv-file (one of: events ' +
            '[VEVENT], todos [VTODO], alarms [VALARM], journals [VJOURNAL], ' +
            'freebusy-indicators [VFREEBUSY]); if no component is specified ' +
            'events [VEVENT] are assumed to be the input / desired output',
        type=str,
        default='VEVENT')
    args = parser.parse_args()

    tool = ICalTool()

    tool.load(args.file, component=args.component)

    for arg, value in args.ordered_args:
        if arg == 'output':
            tool.write(value, component=args.component)
        elif arg == 'filter':
            tool.filter(value)

if __name__ == '__main__':
    main()

