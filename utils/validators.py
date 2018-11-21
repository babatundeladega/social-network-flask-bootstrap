import re

from lepl.apps.rfc3696 import Email

from app.constants import (
    MAX_USER_BIO_LENGTH, MIN_USER_BIO_LENGTH, MIN_PASSWORD_LENGTH)
from app.errors import BadRequest


def check_address_field(value):
    required_keys = {'street_address', 'lga', 'town', 'country', 'province',
        'state', 'zip_code'}

    missing_required_keys = required_keys - set(value.keys())

    if missing_required_keys:
        raise BadRequest(
            '{} must be included in `address` fields'.format(
                missing_required_keys)
        )


def check_amount_field(value):
    try:
        float(value)
    except ValueError:
        raise BadRequest('{} is an invalid amount'.format(value))


def check_bio_field(value):
    min_value = min(len(value), MIN_USER_BIO_LENGTH)
    max_value = max(len(value), MAX_USER_BIO_LENGTH)

    if min_value != MIN_USER_BIO_LENGTH:
        raise BadRequest('Bio must be at least 4 characters')

    if max_value != MAX_USER_BIO_LENGTH:
        raise BadRequest('Bio must be less than 140 characters')

    return min_value == max_value


def check_boolean_field(value):
    if not type(value) is bool:
        raise BadRequest('Boolean expected, not {}'.format(value))


def check_coordinate_field(latitude=None, longitude=None):
    if latitude is not None and not -90 < latitude < 90:
        raise BadRequest('Latitude is invalid')

    if longitude is not None and not -180 < longitude < 180:
        raise BadRequest('Longitude is invalid')


def check_email_field(value):
    validator = Email()
    if not validator(value):
        raise BadRequest('`email` {} is invalid.'.format(value))


def check_field_length(value, length, _greater=True, _lesser=False):
    if _greater and len(value) < length:
        raise BadRequest(
            'Field must be greater than {} characters'.format(length))

    if _lesser and len(value) > length:
        raise BadRequest(
            'Field must be lesser than {} characters'.format(length))


def check_password_field(value):
    return len(value) >= MIN_PASSWORD_LENGTH


def check_phone_field(value):
    if value is None:
        return

    value = value.strip().strip('+').replace(' ', '').replace(
        '-', '')

    try:
        if not value.isdigit():
            raise BadRequest('Phone number is invalid.')

        if len(value) == 10 and not value.startswith('0'):
            value = '234' + value
        elif len(value) == 11 and value.startswith('0'):
            value = '234' + value[1:]
        elif value.startswith('234') and len(value) == 13:
            pass
        else:
            raise BadRequest('Phone number is invalid.')

        return value

    except:
        raise BadRequest('Phone number is invalid.')


def check_url_field(value):
    if value is None:
        return

    return


def check_username_field(value):
    regex_ = r'^[a-zA-Z0-9_.]+$'

    pattern = re.compile(regex_)

    if not pattern.match(value):
        raise BadRequest(
            "Username can have only '_', '.' and alphanumeric characters")
