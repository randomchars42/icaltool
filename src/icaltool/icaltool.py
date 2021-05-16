#!/usr/bin/env python3
import csv
import logging
import logging.config

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

    def csv_load(self, file_name, component,
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

    def csv_write(self, file_name, component = 'VEVENT'):
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

def main():
    logging.config.dictConfig(log.config)
    tool = ICalTool()
    tool.ical_load('icstool/Eike.ics')
    tool.ical_write('icstool/Eike_test.ics')
    tool.csv_write('icstool/Eike_test.csv')
    #tool.csv_load('icstool/Eike_test.csv', 'VEVENT')
    #tool.csv_write('icstool/Eike_test2.csv')
    #tool.ical_write('icstool/Eike_test2.ics')

if __name__ == '__main__':
    main()
