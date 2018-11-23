from flask.views import MethodView

from .authentication import user_auth_required
from app.errors import BadRequest, ResourceNotFound
from app.models import Conversation, User
from utils.response_helpers import (
    api_created_response,
    api_deleted_response,
    api_success_response)
from utils.contexts import get_current_request_data, get_current_user


class ConversationsView(MethodView):
    @staticmethod
    def create_conversation(params):
        conversation = Conversation()
        conversation.save()

        for user in params['users']:
            conversation.users.append(user)

        return conversation

    @staticmethod
    def edit_conversation(conversation, params):
        users = params.get('users')
        if users is not None:
            map(lambda user: conversation.users.remove(user),
                conversation.users)
            map(lambda user: conversation.users.append(user),
                users)


    def __check_conversation_creation_params(self, params):
        users = params.get('users')
        users_ = None

        if users is not None:
            users_ = []

            for username in users:
                try:
                    user = User.get_not_deleted(username=username)
                except:
                    raise ResourceNotFound(
                        'User `{}` not found'.format(username))

                users_.append(user)

        return dict(
            users=users_
        )

    def __validate_conversation_creation_params(self, request_data):
        required_params = {'users'}
        missing_required_params = required_params - set(request_data.keys())

        if missing_required_params:
            raise BadRequest('{} is missing'.format(missing_required_params))

        return self.__check_conversation_creation_params(request_data)

    def __validate_conversation_edit_params(self, request_data):
        return self.__check_conversation_creation_params(request_data)


    @user_auth_required()
    def post(self):
        """Create a conversation"""
        request_data = get_current_request_data()

        params = self.__validate_conversation_creation_params(request_data)

        conversation = self.create_conversation(params)

        return api_created_response(conversation.as_json())

    @user_auth_required()
    def get(self):
        """Get the conversations a user is participating in"""
        user = get_current_user()

        return api_success_response(
            [conversation.as_json() for conversation in user.conversations]
        )

    @user_auth_required()
    def patch(self, conversation_uid):
        """Update a conversation"""
        request_data = get_current_request_data()

        params = self.__validate_conversation_edit_params(request_data)

        conversation = Conversation.get_not_deleted(uid=conversation_uid)
        if conversation is None:
            raise ResourceNotFound('Conversation not found')

        self.edit_conversation(conversation, params)

    @user_auth_required()
    def delete(self, conversation_uid):
        """Delete a conversation"""
        conversation = Conversation.get_not_deleted(uid=conversation_uid)

        if conversation is None:
            raise ResourceNotFound('Conversation not found')

        conversation.delete()

        return api_deleted_response()
