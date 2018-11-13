from functools import wraps

from flask import current_app, request
from jwt import PyJWTError, ExpiredSignatureError
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.exceptions import JWTExtendedException

from app import errors, logger
from app.models import User


def _do_basic_auth():
    # Generate auth token

    auth = request.authorization
    if not auth:
        raise errors.BadRequest('Missing authentication credentials.')

    user = User.get_for_auth(username=auth.username)
    if user is not None:
        if user.verify_password(auth.password):
            return user

    logger.error('Username or password authentication failed.')
    raise errors.UnsuccessfulAuthentication


def _do_bearer_auth():
    # Validate auth token

    try:
        verify_jwt_in_request()

    except ExpiredSignatureError:
        raise errors.TokenExpired

    except JWTExtendedException as err:
        logger.critical(
            'JWTExtendedException: {}'.format(err), exc_info=True)
        raise errors.InvalidAuthToken

    except PyJWTError as err:
        logger.critical('PyJWTError: {}'.format(err), exc_info=True)
        raise errors.InvalidAuthToken

    return User.get_for_auth(username=get_jwt_identity())


def _authenticate_user(obtaining_token):
    if obtaining_token:
        user = _do_basic_auth()
    else:
        user = _do_bearer_auth()

    if user is None:
        raise errors.UnsuccessfulAuthentication

    if not user.is_deleted():
        raise errors.DeletedResource

    return user


def auth_required(obtaining_token=False):
    """Do User authentication.

    Use different authentication strategies to determine the authorization of
    the accessing User
    """
    def view_func_decor(view_func):

        @wraps(view_func)
        def decorated_func(*args, **kwargs):
            app = current_app
            auth_requirement_enabled = app.config['AUTH_REQUIREMENT_ENABLED']

            if auth_requirement_enabled:
                _authenticate_user(obtaining_token=obtaining_token)
            else:
                print(
                    (('FLAG!!! ' * 5) + '\nSkipping Auth Checks! Not Safe for '
                                        'Production!!!\n') * 10)

                user = User.get_for_auth(id=1)
                print('Authenticated User: <%r; [ID: %r]>' % (user.username,
                                                              user.id))

            return view_func(*args, **kwargs)

        return decorated_func

    return view_func_decor

