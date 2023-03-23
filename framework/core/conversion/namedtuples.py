"""Defines named tuples."""
from collections import namedtuple

Term = namedtuple('Term', ['org_id', 'term_id', 'start_date', 'end_date'])

PersonalInformation = namedtuple(
    'PersonalInformation', ["first_name", "last_name", "sex", "profile_image"])
