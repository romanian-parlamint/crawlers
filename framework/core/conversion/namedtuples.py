"""Defines named tuples."""
from collections import namedtuple

Event = namedtuple('Event', ['org_id', 'event_id', 'start_date', 'end_date'])

PersonalInformation = namedtuple(
    'PersonalInformation', ["first_name", "last_name", "sex", "profile_image"])
