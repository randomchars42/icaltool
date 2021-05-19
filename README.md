# ICalTool

## tl;dr;

* **`.ics` -> (filter) -> `.ics`**: `icaltool INPUTFILE.ics -f "FILTERRULES" -o OUTPUTFILE.ics`
* **`.ics` -> (filter) -> `.csv`**: `icaltool INPUTFILE.ics -f "FILTERRULES" -o OUTPUTFILE.csv`
* **`.csv` -> (filter) -> `.ics`**: `icaltool INPUTFILE.csv -f "FILTERRULES" -o OUTPUTFILE.ics`
* **`.csv` -> (filter) -> `.csv`**: `icaltool INPUTFILE.csv -f "FILTERRULES" -o OUTPUTFILE.csv`

and more ...

## What?

Work with calendar data, either in the ical format (`.ics`) or from a spreadsheet (`.csv`).

Allows you to filter by properties, e.g., start date (`DTSTART`), end date (`DTEND`)..., or component type, e.g., event (`VEVENT`), todo (`VTODO`), ... .

The resulting data can be stored either as ical (`.ics`) or spreadsheet (`.csv`).

## How?

`icaltool INPUTFILE [-f FILTERRULES] [-o OUTPUTFILE] [-c COMPONENT]`

`icaltool` takes one input file, the file type is inferred from the ending (`.ics` or `.csv`).

It can now store the parsed data into a file (`-o OUTPUTFILE`). Again, the file type is inferred by its ending (`.ics` or `.csv`).

Additionally, it can filter (`-f FILTERRULES`) the parsed data using one or more rules, see *Filtering* below.

If you read from or write to a `.csv`-file you need to specify a component (event [`VEVENT`], todo [`VTODO`], journal [`VJOURNAL`], alarm [`VALARM`], ...), since in a `.csv`-file only one component can be represented. If you don't specify a component, events [`VEVENT`], are assumed.

**Note** that with `-f FILTERRULES` and `-o OUTPUTFILE` the order of those two arguments matter: they are parsed in order! If you output (`-o OUTPUTFILE`) a file before filtering (`-f FILTERULES`), the unfiltered data gets written to the file and the filtered data ends up where the null-pointer leads to.

**Example:**

`icaltool INPUTFILE.ics -o OUTPUTFILE1.csv -f "COMPONENT:+VEVENT;DTSTART:+2015to2020" -o OUTPUTFILE2.ics`

 1. read `INPUTFILE.ics`
 2. write the (**unfiltered**) data to `OUTPUTFILE1.csv`, note that since `-c COMPONENT` is not specified only events [`VEVENTS`] will be stored in the file
 3. filter the data using `COMPONENT:+VEVENT;DTSTART:+2015to2020` (see *Filtering* below)
 4. write the **filtered** data to `OUTPUTFILE2.csv`

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
 - ... attended by `john.doe@mail.domain`:
   `DTSTART:+2015-10to2017-11;ATTENDEE:+john.doe@mail.domain`
 - ... but not by `jane.doe@mail.domain`:
   `...;ATTENDEE:+john.doe@mail.domain|-jane.doe@mail.domain`

So your full rule might be:

`COMPONENT:+VEVENT;DTSTART:+2015-10to2017-11;ATTENDEE:+john.doe@mail.domain|-jane.doe@mail.domain`

## Notes

Though the script runs generally quite stable, the odd glitch can happen (especially with `"` in `.csv`-files) so **please, work on a copy** ;) .

**Beware of `,`, `;` and `|`** when using regular expressions as those currently do not get escaped properly.

**Filtering by timespans** currently does take time zones into consideration but this should only affect rather weird edge-cases.

Conversion from `.ics` to `.csv` tends to be lossy, even if the programme is generally written to preserve attributes and parameters it doesn't know. For example, alarms / reminders are a nested component which do currently not translate into something represented in the `.csv`-file. Furthermore, the calendar information stored in `VTIMEZONE`, `STANDARD` and `DAYLIGHT` will be lost.

## Extendability

Each property or component is or can easily be represented by a class derived from a base class (`datatypes.Property`) which generally only copies the data. If you need to manipulate a certain property you need only derive your own class (look at `datatypes.DateTime` for an example).
