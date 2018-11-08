import simplejson
from flask import make_response

from utils.contexts import (
    get_current_api_ref, get_current_request_args, get_current_request_data,
    get_current_request_url)


def _make_api_response(
        data: dict, meta, message, headers:dict, cookies:dict,
        status_code: int, status):

    response_body = simplejson.dumps({
        'api_ref': get_current_api_ref(),
        'meta': meta,
        'message': message,
        'status': status,
        'your_request': {
            'url': get_current_request_url(),
            'query_args': get_current_request_args(),
            'payload': get_current_request_data()
        },
        'your_response': data
    })

    resp = make_response(response_body, status_code)

    if headers is not None:
        for key, value in headers.items():
            resp.headers[key] = value

    if cookies is not None:
        for key, value in cookies.items():
            resp.set_cookie(key, value)

    return resp


def api_created_response(data=None, meta=None, message=None, headers=None,
        cookies=None, status_code=201):

    status = 'SUCCESS'

    return _make_api_response(
        data, meta, message, headers, cookies, status_code, status)


def api_deleted_response(data=None, meta=None, message=None, headers=None,
        cookies=None, status_code=204):

    status = 'SUCCESS'

    return _make_api_response(
        data, meta, message, headers, cookies, status_code, status)


def api_success_response(data=None, meta=None, message=None, headers=None,
        cookies=None, status_code=200):

    status = 'SUCCESS'

    return _make_api_response(
        data, meta, message, headers, cookies, status_code, status)


def api_failure_response(code, error_msg, response_meta=None):

    return _make_api_response(
        status='FAILURE', data={}, message=error_msg,
        status_code=code, meta=response_meta, cookies={},
        headers={})
