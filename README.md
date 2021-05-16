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

## Notice

Though the script runs generally quite stable, the odd glitch can happen (especially with `"` in `.csv`) so **please, work on a copy** ;) .

Conversion from `.csv` to `.ics` tends to be lossy, even if the programme is generally written to preserve attributes and parameters it doesn't know.

## Extendability

Each property or component is or can easily be represented by a class derived from a base class (`datatypes.Property`) which generally only copies the data. If you need to manipulate a certain property you need only derive your own class (look at `datatypes.DateTime` for an example).
