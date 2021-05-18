# ICalTool

## tl;dr;

* `.ics` -> (filter) -> `.ics`
* `.ics` -> (filter) -> `.csv`
* `.csv` -> (filter) -> `.ics`
* `.csv` -> (filter) -> `.csv`

## What?

Work with calendar data, either in the ical format (`.ics`) or from a spreadsheet (`.csv`).

Allows you to filter by properties, e.g., start date (`DTSTART`), end date (`DTEND`)..., or component type, e.g., event (`VEVENT`), todo (`VTODO`), ... .

The resulting data can be stored either as ical (`.ics`) or spreadsheet (`.csv`).

## How?

### Filtering

Filters can be applied specifying `-f RULES` when using the command line or using `ICalTool.filter(RULES)` after `ICalTool.load(FILE)`.

 1. `RULES` start with the target, e.g. `COMPONENT` for filtering components or `DTSTART` for filtering the start time, followed by a ':'
 2. next follows either a `+` if only items matching the term should be kept or a `-` if only items not matching the terms are to be kept
 3. now comes the term - generally a string that will be searched for in the value, with 3 exceptions:
      * for the target `COMPONENT` you specify a list of components, e.g., `VEVENT`, `VTODO`, `VJOURNAL`, `VALARM` ...
      * if your search term is `re(YOURREGULAEXPRESSION)` then `YOURREGULAREXPRESSION` will be matched using `re.match`
      * if you are targeting a property containing a date, i.e., start time (`DTSTART`), end time (`DTEND`), `DTSTAMP`, creation date (`CREATED`) or time of last modification (`LAST-MODIFIED`), you can specify a year (`YYYY`), year and month (`YYYY-MM`), a date (`YYYY-MM-DD`) or a range (using `to`, see examples)
 4. you may concatenate rules for multiple targets using `:`
 5. you may concatenate rules for the same targets using `|`

**Examples:**

 - keep only events:
   `COMPONENT:+VEVENT`
 - filter out all events:
   `COMPONENT:-VEVENT`
 - filter out all events and alarms
   `COMPONENT:-VEVENT,VALARM`
 - filter out all components with a start date between 2015 and 2017:
   `DTSTART:-2015to2017`
 - keep only components with a start date between 2015-10 and 2017-11:
   `DTSTART:+2015-10to2017-11`
 - ... attended by john.doe@mail.domain:
   `DTSTART:+2015-10to2017-11;ATTENDEE:+john.doe@mail.domain`
 - ... but not by jane.doe@mail.domain:
   `...;ATTENDEE:+john.doe@mail.domain|-jane.doe@mail.domain`

So your full rule might be:

`COMPONENT:+VEVENT;DTSTART:+2015-10to2017-11;ATTENDEE:+john.doe@mail.domain|-jane.doe@mail.domain`

## Notice

Though the script runs generally quite stable, the odd glitch can happen (especially with `"` in `.csv` files) so **please, work on a copy** ;) .

Conversion from `.csv` to `.ics` tends to be lossy, even if the programme is generally written to preserve attributes and parameters it doesn't know.

## Extendability

Each property or component is or can easily be represented by a class derived from a base class (`datatypes.Property`) which generally only copies the data. If you need to manipulate a certain property you need only derive your own class (look at `datatypes.DateTime` for an example).
