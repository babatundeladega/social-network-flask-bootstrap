import random
import re
import shortuuid

from flask import current_app
from itsdangerous import URLSafeTimedSerializer

from app.constants import EMAIL_CONFIRMATION_LINK_LIFESPAN


def confirm_token(token, expiration=EMAIL_CONFIRMATION_LINK_LIFESPAN):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=current_app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )

    except:
        return False

    return email


def extract_hash_tags_for_text(text):
    text_splitted = text.split(' ')

    return list(
        filter(lambda x: trim_hash_tag(x.startswith('#')), text_splitted)
    )


def generate_phone_verification_code():
    return random.randint(10000, 99999)


def generate_email_confirmation_token(email_address):
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(
        email_address, salt=current_app.config['SECURITY_PASSWORD_SALT'])


def generate_unique_reference():
    return shortuuid.uuid()


def trim_hash_tag(hash_tag):
    pattern = re.compile('[\W_]+')

    pattern.sub('', hash_tag)
