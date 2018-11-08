import json
from functools import wraps

from flask import g, request

from app import errors
from app.constants import SUPPORTED_HTTP_METHODS
from utils.contexts import (
    get_current_api_log, get_current_request_headers,
    get_current_user)


def _update_api_log(api_log_id, request_method, request_url, user_id,
        response_data=None, request_headers=None):
    """Update the API log on completing request handling."""
    # from application.core.models import APILog

    endpoint = (
        '{HTTP_METHOD} {ENDPOINT}'.format(
            HTTP_METHOD=request_method,
            ENDPOINT=request_url
        )
    )

    # api_log = APILog.query.get(api_log_id)
    api_log = get_current_api_log()  # Stub until task queue (Celery) is added
    # if api_log is None:
    #     logger.error('API activity is None. yourResponse: '
    #                  '{0}'.format(repr(response_data)))
    #     return False

    api_log.update(
        created_by_id=user_id,
        request_headers=str(request_headers),
        response_data=str(response_data),
        endpoint=endpoint,
        error_msg='API activity logging update failed!')

    # return True


def before_every_request():
    """Do some necessary setup before handling any request."""

    g.request_cost = 0

    try:
        # DB-persist new API activity
        g.api_log = get_current_api_log()
    except:
        raise errors.APIError(
            log_message='Error persisting API activity to DB!')


def add_cors_support(f):
    allowed_methods = ', '.join(SUPPORTED_HTTP_METHODS)

    @wraps(f)
    def decorated_func(*args, **kwargs):
        response = f(*args, **kwargs)

        response.headers['Access-Control-Allow-Origin'] = (
            request.headers.get('Origin', '*')
        )
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Allow-Methods'] = allowed_methods
        response.headers['Access-Control-Allow-Headers'] = (
            request.headers.get('Access-Control-Request-Headers',
                                'Authorization')
        )

        return response

    return decorated_func


@add_cors_support
def after_every_request(response):
    """Do necessary operations after every request."""
    # Update API activity log: Save response payload
    from app.models import APILog

    try:
        response_data = response.response[0]
    except IndexError:
        response_data = None

    user = get_current_user()

    _update_api_log(
        api_log_id=get_current_api_log().id,
        request_method=request.method,
        request_url=request.url,
        user_id=getattr(user, 'id', None),
        response_data=response_data,
        request_headers=get_current_request_headers()
    )

    if user:  # and g.app.ownership != 'Proprietary':
        users_today_requests = APILog.query.filter_by(
            created_by_id=g.user.id
        ).count()

        if users_today_requests > g.user.pricing.toll_free_daily_requests:
            g.request_cost += g.user.pricing.request_cost

        user.record_request_cost(g.request_cost)

    return response
