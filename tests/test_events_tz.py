from util import parse_yaml

from yaml2ics import event_from_yaml

def test_event_with_tz():
    event = event_from_yaml(
        parse_yaml(
            '''
            summary: Event of the Century
            begin: 1970-01-01 02:00:00 -02:00
            duration:
              minutes: 30
            description: |
              Meet the team on the northern side of the field.
            '''
        )
    )

    event_str = event.serialize()
    assert 'DURATION:PT30M' in event_str
    assert 'TZID="UTC-02:00":19700101T020000' in event_str
