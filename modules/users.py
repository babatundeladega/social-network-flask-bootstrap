from flask.views import MethodView

from .authentication import app_auth_required
from app.errors import BadRequest, ResourceNotFound
from app.models import Blob, User
from utils.contexts import get_current_request_data
from utils.response_helpers import (
    api_created_response, api_deleted_response, api_success_response)
from utils.validators import (
    check_bio_field, check_email_field, check_password_field, check_phone_field,
    check_username_field)


class UsersView(MethodView):
    @staticmethod
    def create_new_user(params):
        user = User(
            **params
        )

        user.save()

        return user

    @staticmethod
    def edit_existing_user(user, params):
        user.update(**params)

        return user


    def __check_user_params(self, request_data):
        username = request_data.get('username')
        if username is not None:
            check_username_field(username)

        password = request_data.get('password')
        if password is not None:
            check_password_field(password)

        bio = request_data.get('bio')
        if bio is not None:
            check_bio_field(bio)

        phone = request_data.get('phone')
        if phone is not None:
            check_phone_field(phone)

        email = request_data.get('email')
        if email is not None:
            check_email_field(email)

        profile_photo_uid = request_data.get('profile_photo_uid')
        profile_photo = Blob.get_active(uid=profile_photo_uid)
        if profile_photo is None:
            raise ResourceNotFound('Profile photo not found')

        return dict(
            username=username, password=password, bio=bio, email=email,
            phone=phone, profile_photo=profile_photo)

    def __validate_user_creation_params(self, request_data):
        required_params = {'username', 'password'}

        missing_required_params = required_params - set(request_data.keys())
        if missing_required_params:
            raise BadRequest(
                '{} required to create a user are missing'.format(
                    required_params)
            )

        return self.__check_user_params(request_data)

    def __validate_user_update_params(self, request_data):
        return self.__check_user_params(request_data)


    @app_auth_required()
    def post(self):
        request_data = get_current_request_data()

        params = self.__validate_user_creation_params(request_data)

        user = self.create_new_user(params)

        return api_created_response(user.as_json())

    @app_auth_required()
    def get(self, username):
        user = User.get_active(username=username)
        if user is None:
            raise ResourceNotFound('User not found')

        return api_success_response(user.as_json())

    @app_auth_required()
    def patch(self, username):
        request_data = get_current_request_data()

        params = self.__validate_user_update_params(request_data)

        user = User.get_active(username=username)
        if user is None:
            raise ResourceNotFound('User not found')

        user = self.edit_existing_user(user, params)

        return api_success_response(user.as_json())

    @app_auth_required()
    def delete(self, username):
        user = User.get_active(username=username)
        if user is None:
            raise ResourceNotFound('User not found')

        user.delete()

        return api_deleted_response()
