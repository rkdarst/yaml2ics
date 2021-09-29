import io
import textwrap

from util import parse_yaml

from yaml2ics import events_to_calendar, files_to_calendar


def test_calendar_structure():
    cal = events_to_calendar([])
    cal_str = cal.serialize()
    assert cal_str.startswith('BEGIN:VCALENDAR')
    assert cal_str.endswith('END:VCALENDAR')

def test_calendar_event():
    cal = files_to_calendar(
        [io.StringIO(textwrap.dedent(
            '''
            events:
              - summary: Earth Day
                begin: 2021-04-22
                url: https://earthday.org
                location: Earth
            '''
        ))]
    )
    cal_str = cal.serialize()
    assert cal_str.startswith('BEGIN:VCALENDAR')
    assert 'SUMMARY:Earth Day' in cal_str
    assert cal_str.endswith('END:VCALENDAR')


def test_calendar_yaml_default_tz():
    cal = files_to_calendar(
        [io.StringIO(textwrap.dedent(
            '''
            meta:
              tz: Europe/Helsinki
            events:
            - summary: Event of the Century
              begin: 1970-01-01 00:00:00
              duration:
                minutes: 30
              description: |
                Meet the team on the northern side of the field.
            '''
        ))]
    )

    cal_str = cal.serialize()
    print(cal_str)
    assert cal_str.startswith('BEGIN:VCALENDAR')
    assert 'Europe/Helsinki:19700101T000000' in cal_str
