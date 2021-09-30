import yaml
import sys
import os
from datetime import datetime

import ics
import dateutil
import dateutil.rrule


interval_type = {
    'seconds': dateutil.rrule.SECONDLY,
    'minutes': dateutil.rrule.MINUTELY,
    'hours': dateutil.rrule.HOURLY,
    'days': dateutil.rrule.DAILY,
    'weeks': dateutil.rrule.WEEKLY,
    'months': dateutil.rrule.MONTHLY,
    'years': dateutil.rrule.YEARLY
}


def event_from_yaml(event_yaml: dict) -> ics.Event:
    d = event_yaml
    repeat = d.pop('repeat', None)

    # Strip all string values, since they often end on `\n`
    for key in d:
        d[key] = d[key].strip() if isinstance(d[key], str) else d[key]

    # See https://icspy.readthedocs.io/en/stable/api.html#event
    #
    # Keywords:
    # name, begin, end, duration, uid, description, created, last_modified,
    # location, url, transparent, alarms, attendees, categories, status,
    # organizer, geo, classification
    event = ics.Event(**d)

    # Handle all-day events
    if not ('duration' in d or 'end' in d):
        event.make_all_day()

    if repeat:
        interval = repeat['interval']

        if not len(interval) == 1:
            print('Error: interval must specify seconds, minutes, hours, days, weeks, months, or years only')
            sys.exit(-1)

        interval_measure = list(interval.keys())[0]
        if interval_measure not in interval_type:
            print('Error: expected interval to be specified in seconds, minutes, hours, days, weeks, months, or years only')
            sys.exit(-1)

        if 'until' not in repeat:
            print('Error: must specify end date for repeating events')
            sys.exit(-1)

        event.end = d.get('end', None)

        rrule = dateutil.rrule.rrule(
            freq=interval_type[interval_measure],
            until=repeat.get('until'),
            dtstart=d['begin']
        )

        rrule_lines = str(rrule).split('\n')
        rrule_dtstart = [line for line in rrule_lines if line.startswith('DTSTART')][0]
        rrule_dtstart = rrule_dtstart + 'Z'
        rrule_rrule = [line for line in rrule_lines if line.startswith('RRULE')][0]

        event.extra.append(ics.ContentLine(rrule_rrule))

    event.dtstamp = datetime.utcnow().replace(tzinfo=dateutil.tz.UTC)
    return event


def events_to_calendar(events: list) -> str:
    cal = ics.Calendar()
    for event in events:
        cal.events.append(event)
    return cal

def files_to_calendar(files: list) -> ics.Calendar:
    """'main' function: list of files to our result"""
    all_events = [ ]
    for f in files:
        # Load raw data
        if hasattr(f, 'read'):
            calendar_yaml = yaml.load(f.read(), Loader=yaml.FullLoader)
        else:
            calendar_yaml = yaml.load(open(f, 'r'), Loader=yaml.FullLoader)
        # Find any possible metadata
        meta = None
        tzname = None
        if 'meta' in calendar_yaml:
            tzname = calendar_yaml['meta'].get('tz')
        # Convert events
        for event in calendar_yaml['events']:
            all_events.append(event_from_yaml(event))
    calendar = events_to_calendar(all_events)
    if tzname:
        import ics.timespan
        calendar.normalize(dateutil.tz.gettz(tzname),
                           ics.timespan.NormalizationAction.REPLACE)
    return calendar


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: yaml2ics.py FILE1.yaml FILE2.yaml ...')
        sys.exit(-1)

    files = sys.argv[1:]
    for f in files:
        if not os.path.isfile(f):
            print(f'Error: {f} is not a file')
            sys.exit(-1)

    calendar = files_to_calendar(files)

    print(calendar.serialize())
