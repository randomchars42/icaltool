#!/usr/bin/env python3

import time
import logging

logger = logging.getLogger(__name__)

class Component:
    name = 'COMPONENT'
    defined_properties = {}
    delimiter = '@@'

    def __init__(self):
        self._components = []
        self._properties = []

    def csv_parse(self, component, rows, column_mapping):
        for row in rows:
            current_component = globals()[component]()
            try:
                for property_name, column_index in column_mapping.items():
                    values = row[column_index]
                    for value in values.split(self.__class__.delimiter):
                        # split multiple values by delimiter and create a
                        # property instance per value
                        current_component._parse_property(
                            property_name, value, 'csv_parse')
                self._components.append(current_component)
            except ValueError:
                # there is no required property, which can have multiple values
                # https://upload.wikimedia.org/wikipedia/commons/c/c0/ICalendarSpecification.png
                logger.warning(
                    'dropped row due to missing or malformed required value')

    def ical_parse(self, lines):
        current_component = None
        logger.debug('begin parsing {}'.format(self.name))
        for line in lines:
            if current_component:
                # the line belongs to the current_component so:
                # 1. it may end it
                if line[:4] == "END:" and line[4:] == current_component.name:
                    if not drop_current_component:
                        current_component.ical_parse(recorded)
                        self._components.append(current_component)
                    else:
                        logger.warning('dropped {} due to an error.'.format(
                            current_component.name))
                    logger.debug('finished recording {}'.format(
                        current_component.name))
                    current_component = None
                # 2. belong to the current_component
                else:
                    recorded.append(line)
            else:
                # the line does not yet belong to a component other than the
                # calling container so it may
                # 1. begin a new component
                if line[:6] == 'BEGIN:':
                    # create an instance for the component
                    current_component = globals()[line[6:]]()
                    # and start recording lines
                    recorded = []
                    drop_current_component = False
                    logger.debug('recording new {}'.format(
                        current_component.name))
                # 2. be a property of the calling component
                else:
                    try:
                        self._ical_parse_line(line)
                    except ValueError:
                        # required property missing / not parseable
                        drop_current_component = True

        logger.debug('finished parsing {}'.format(self.name))

    def _ical_parse_line(self, line):
        # split line:
        # NAME:VALUE                  -> [0] NAME     [1] VALUE
        # NAME;PARAM=PARAMVALUE:VALUE -> [0] NAME     [1] PARAM=PARAMVALUE:VALUE
        position = line.find(';')
        position2 = line.find(':')

        if position > -1 and position < position2:
            name = line[:position]
            content = line[position:]
        else:
            name = line[:position2]
            content = line[position2:]

        if name == '':
            logger.warning('ignoring malformatted line "{}"'.format(line))

        self._parse_property(name, content, "ical_parse")

    def _parse_property(self, name, content, function_name):
        # the property may be:
        try:
            # 1. known (there is an entry in self.__class__.defined_properties)
            required, property_class = self.__class__.defined_properties[name]
        except KeyError:
            # 2. unknown
            if not name == '':
                # add the property to the list using "accept" and `Property`
                prop = [0, 'Property']
                self.__class__.defined_properties[name] = prop
                logger.warning('unknown property "{}" added to {}'.format(
                    name, self.name))

        if content == '':
            if required == 1:
                # property is required
                logger.warning('required property "{}" missing'.format(name))
                raise ValueError
            else:
                return

        if not required == -1:
            # property is required or accepted
            try:
                property_object = globals()[property_class](name)
                function = getattr(property_object, function_name)
                function(content)
            except ValueError:
                if required == 1:
                    logger.warning(
                        'required property "{}" not parseable ("{}")'.format(
                            name, content))
                    raise ValueError
                else:
                    # ignore the property
                    logger.warning('property "{}" not parseable ("{}")'.format(
                        name, content))
                    property_object = None
        else:
            # property will be ignored
             property_object = None

        if not property_object is None:
            self._properties.append(property_object)

    def csv_write(self, component):
        if not self.__class__.name == component:
            return ''
        columns = []
        for def_prop, attributes in self.__class__.defined_properties.items():
            if attributes[0] == 2:
                continue
            values = ''
            for prop in self._properties:
                if prop.name == def_prop:
                    # see if the component entity has this property
                    if values == '':
                        values = prop.csv_write()
                    else:
                        # in case of multiple allowed values try to append to
                        # an existing value
                        values += self.__class__.delimiter + prop.csv_write()
            columns.append(values)
        return ','.join(columns)

    def ical_write(self):
        lines = []
        lines.append('BEGIN:{}'.format(self.name))
        for prop in self._properties:
            lines.append(prop.ical_write())
        for component in self._components:
            lines.extend(component.ical_write())
        lines.append('END:{}'.format(self.name))
        return lines

class VCALENDAR(Component):
    name = 'VCALENDAR'
    defined_properties = {
        'PRODID': [0, 'Property'],
        'VERSION': [0, 'Property']}

    def csv_write(self, component):
        lines = []
        for entity in self._components:
            line = entity.csv_write(component)
            if not line == '':
                lines.append(line)
        return lines

class VEVENT(Component):
    name = 'VEVENT'
    defined_properties = {
        # handle (0: accept, 1: require, -1: ignore), target class
        'DTSTART': [1, 'DateTime'],
        'DTEND': [1, 'DateTime'],
        'DTSTAMP': [1, 'DateTime'],
        'ORGANIZER': [-1, 'Property'],
        'UID': [0, 'Property'],
        'ATTENDEE': [-1, 'Property'],
        'CREATED': [0, 'DateTime'],
        'DESCRIPTION': [0, 'Property'],
        'LAST-MODIFIED': [0, 'DateTime'],
        'LOCATION': [0, 'Property'],
        'SEQUENCE': [0, 'Property'],
        'SUMMARY': [0, 'Property'],
        'CATEGORIES': [0, 'Property'],
        'CLASS': [0, 'Property'],
        'ATTACH': [0, 'Property'],
        'TRANSP': [0, 'Property'],
        'RRULE': [0, 'Property'],
        'EXDATE': [0, 'Property'],
        'STATUS': [0, 'Property'],
        'X-ALT-DESC': [-1, 'Property'],
        'X-APPLE-DEFAULT-ALARM': [-1, 'Property'],
        'X-APPLE-TRAVEL-ADVISORY-BEHAVIOR': [-1, 'Property'],
        'X-EVOLUTION-ALARM-UID': [-1, 'Property'],
        'X-LIC-ERROR': [-1, 'Property'],
        'X-MOZ-GENERATION': [-1, 'Property'],
        'X-MOZ-LASTACK': [-1, 'Property'],
        'X-MOZ-RECEIVED-SEQUENCE': [-1, 'Property'],
        'X-MOZ-RECEIVED-DTSTAMP': [-1, 'Property'],
        'X-WR-ALARMUID': [-1, 'Property']}

class VTODO(Component):
    name = 'VTODO'
    defined_properties = {}

class VJOURNAL(Component):
    name = 'VJOURNAL'
    defined_properties = {}

class VFREEBUSY(Component):
    name = 'VFREEBUSY'
    defined_properties = {}

class VTIMEZONE(Component):
    name = 'VTIMEZONE'
    defined_properties = {
        'TZID': [0, 'Property']}

class VALARM(Component):
    name = 'VALARM'
    defined_properties = {
        'ACTION': [0, 'Property'],
        'ATTACH': [0, 'Property'],
        'TRIGGER': [0, 'Property'],
        'UID': [0, 'Property'],
        'DESCRIPTION': [0, 'Property'],
        'X-LIC-ERROR': [-1, 'Property'],
        'X-EVOLUTION-ALARM-UID': [-1, 'Property'],
        'X-WR-ALARMUID': [-1, 'Property'],
        'X-APPLE-DEFAULT-ALARM': [-1, 'Property']}

class STANDARD(Component):
    name = 'STANDARD'
    defined_properties = {
        'TZOFFSETFROM': [0, 'Property'],
        'TZOFFSETTO': [0, 'Property'],
        'TZNAME': [0, 'Property'],
        'DTSTART': [0, 'DateTime'],
        'RRULE': [0, 'Property']}

class DAYLIGHT(Component):
    name = 'DAYLIGHT'
    defined_properties = {
        'TZOFFSETFROM': [0, 'Property'],
        'TZOFFSETTO': [0, 'Property'],
        'TZNAME': [0, 'Property'],
        'DTSTART': [0, 'DateTime'],
        'RRULE': [0, 'Property']}

class Property:
    def __init__(self, name):
        self.name = name
        self.value = None

    def csv_parse(self, value):
        if value[0] == '"' and value[-1] == '"':
            # remove '"' around the value
            value = value[1:-1]
        return self._parse(value)

    def ical_parse(self, value):
        return self._parse(value)

    def _parse(self, value):
        self.value = value
        return self.value

    def get_value(self):
        return self.value

    def csv_write(self):
        return '"{}"'.format(self._write()[1:])

    def ical_write(self):
        return self.name + self._write()

    def _write(self):
        return self.value

class DateTime(Property):
    def __init__(self, name):
        super().__init__(name)
        # 0: invalid
        # 1: date
        # 2: datetime (local)
        # 3: datetime (UTC)
        self.type = 0
        self._tzid = None

    def ical_parse(self, value):
        value = value[1:]
        self.value = self._parse(value)
        return self.value

    def csv_parse(self, value):
        self.value = self._parse(value)
        return self.value

    def _parse(self, value):
        if value[:4] == 'TZID':
            # omit "0" following "TZID"
            tmp = value[5:].split(':', 1)
            self._tzid = tmp[0]
            value = tmp[1]
            del tmp
        elif value[:11] == 'VALUE=DATE:':
            value = value[11:]

        length = len(value)
        if length == 8:
            format_string = '%Y%m%d'
            self.type = 1
        elif length == 15:
            format_string = '%Y%m%dT%H%M%S'
            self.type = 2
        elif length == 16:
            format_string = '%Y%m%dT%H%M%SZ'
            self.type = 3
        elif length == 10:
            format_string = '%Y-%m-%d'
            self.type = 1
        elif length == 17:
            format_string = '%Y-%m-%dT%H%M%S'
            self.type = 2
        elif length == 19:
            format_string = '%Y-%m-%dT%H:%M:%S'
            self.type = 2
        elif length == 18:
            format_string = '%Y-%m-%dT%H%M%SZ'
            self.type = 3
        elif length == 20:
            format_string = '%Y-%m-%dT%H:%M:%SZ'
            self.type = 3
        else:
            format_string = ''
        try:
            self.value = time.strptime(value, format_string)
        except ValueError:
            self.type = None
            logger.info('Could not process ' + value)
            raise ValueError
        return self.value

    def _write(self):
        datetime = ''
        if not self._tzid is None:
            datetime = ';TZID={}'.format(self._tzid)
        if self.type == 0:
            return ''
        elif self.type == 1:
            datetime += time.strftime(':%Y%m%d', self.value)
        elif self.type == 2:
            datetime += time.strftime(':%Y%m%dT%H%M%S', self.value)
        else:
            datetime += time.strftime(':%Y%m%dT%H%M%SZ', self.value)
        return datetime
