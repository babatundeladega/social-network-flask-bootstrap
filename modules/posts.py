from flask.views import MethodView

from .authentication import user_auth_required
from app.constants import MIN_POST_TEXT_LENGTH
from app.errors import BadRequest, ResourceNotFound, UnauthorizedError
from app.models import Blob, Post, User
from utils.contexts import (
    get_current_request_args,
    get_current_request_data,
    get_current_user)
from utils.validators import check_boolean_field, check_field_length
from utils.response_helpers import (
    api_created_response,
    api_deleted_response,
    api_success_response)


class PostsView(MethodView):
    @staticmethod
    def create_post(params):
        post = Post(
            user_id=get_current_user().id,
            **params
        )

        post.save()

        return post

    @staticmethod
    def edit_post(post, params):
        post.update(**params)

        return post


    def __check_post_params(self, request_data):
        comments_enabled = request_data.get('comments_enabled')
        if comments_enabled is not None:
            check_boolean_field(comments_enabled)

        text = request_data.get('text')
        if text is not None:
            check_field_length(text, MIN_POST_TEXT_LENGTH)

        blobs = request_data.get('blobs')
        if not isinstance(blobs, list):
            raise BadRequest('`blobs` must be an array')

        for blob_uid in blobs:
            try:
                Blob.get_active(uid=blob_uid)
            except :
                raise ResourceNotFound('Blob `{}` not found'.format(blob_uid))

        return dict(comments_enabled=comments_enabled, blobs=blobs, text=text)

    def __validate_post_creation_params(self, request_data):
        required_params = {'blobs'}

        missing_required_params = required_params - set(request_data.keys())
        if missing_required_params:
            raise BadRequest(
                '{} required to create a user are missing'.format(
                    required_params)
            )

        return self.__check_post_params(request_data)

    def __validate_post_edit_params(self, params):
        self.__check_post_params(params)


    @user_auth_required()
    def get(self, post_uid=None):
        """Retrieve a post or a list of posts"""
        request_args = get_current_request_args()

        user_uid = request_args.get('user_uid')

        if user_uid is not None:
            user = User.get_active(uid=user_uid)
            if user is None:
                raise ResourceNotFound

        else:
            user = get_current_user()

        if post_uid is not None:
            post = Post.get_active(uid=post_uid, user_id=user.id)
            if post is None:
                raise ResourceNotFound

            return api_success_response(data=post.as_json())

        pagination = Post.get_active(user_id=user.id).paginate()

        return api_success_response(
            [item.as_json() for item in pagination.items],
            meta=pagination.meta
        )

    @user_auth_required()
    def post(self):
        """Create a post"""
        request_data = get_current_request_data()

        params = self.__validate_post_creation_params(request_data)

        post = self.create_post(params)

        return api_created_response(post.as_json())

    @user_auth_required()
    def patch(self, post_uid):
        """Edit a post"""
        request_data = get_current_request_data()

        post = Post.get_active(uid=post_uid)
        if post is None:
            raise ResourceNotFound()

        if post.user != get_current_user():
            raise UnauthorizedError()

        params = self.__validate_post_edit_params(request_data)

        self.edit_post(post, params)

        return api_success_response(post.as_json())

    @user_auth_required()
    def delete(self, post_uid):
        """Delete a post"""
        post = Post.get_active(uid=post_uid)
        if post is None:
            raise ResourceNotFound()

        if post.user != get_current_user():
            raise UnauthorizedError()

        post.delete()

        return api_deleted_response()


class TimelinePostsView(MethodView):
    @user_auth_required()
    def get(self):
        """Get all the posts for a timeline"""
        return
