from flask.views import MethodView

from .authentication import user_auth_required
from app.constants import MIN_POST_TEXT_LENGTH
from app.errors import BadRequest, ResourceNotFound, UnauthorizedError
from app.models import Blob, Location, Post, User
from app.models import followers
from modules.hashtags import HashTagsView
from utils.contexts import (
    get_current_request_args,
    get_current_request_data,
    get_current_user)
from utils.response_helpers import (
    api_created_response,
    api_deleted_response,
    api_success_response)
from utils import extract_hash_tags_for_text, trim_hash_tag
from utils.validators import check_boolean_field, check_field_length


class PostsView(MethodView):
    @staticmethod
    def create_post(params):
        text = params['text']

        extracted_hash_tags = extract_hash_tags_for_text(text)
        hash_tag_orms = map(
            lambda x: HashTagsView.create_hash_tag(x),
            extracted_hash_tags
        )

        post = Post(
            user_id=get_current_user().id,
            **params
        )

        post.save()

        map(
            lambda x: HashTagsView.add_post_to_hash_tag(post, x),
            hash_tag_orms
        )

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

        location_uid = request_data.get('location_uid')
        location = Location.get_active(uid=location_uid)
        if bool(location_uid) != bool(location):
            raise ResourceNotFound('`location_uid` not found')

        request_blobs = request_data.get('blobs')
        if not isinstance(request_blobs, list):
            raise BadRequest('`blobs` must be an array')

        post_slides = []
        for blob_uid in request_blobs:
            try:
                blob = Blob.get_active(uid=blob_uid)
                post_slides.append(blob)
            except :
                raise ResourceNotFound('Blob `{}` not found'.format(blob_uid))

        return dict(
            post_slides=post_slides,
            comments_enabled=comments_enabled,
            location=location,
            text=text)

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
        return self.__check_post_params(params)


    @user_auth_required()
    def get(self, post_uid=None):
        """Retrieve a post or a list of posts"""
        request_args = get_current_request_args()

        user_uid = request_args.get('user_uid')

        if user_uid is not None:
            user = User.get_active(uid=user_uid)
            if user is None:
                raise ResourceNotFound('User not found')

        else:
            user = get_current_user()

        if post_uid is not None:
            post = Post.get_active(uid=post_uid, user_id=user.id)
            if post is None:
                raise ResourceNotFound('Post not found')

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
            raise ResourceNotFound('Post not found')

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
            raise ResourceNotFound('Post not found')

        if post.user != get_current_user():
            raise UnauthorizedError()

        post.delete()

        return api_deleted_response()


class TimelinePostsView(MethodView):
    @user_auth_required()
    def get(self):
        """Get all the posts for a timeline"""
        user = get_current_user()

        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)
        ).filter(
            followers.c.follower_id == user.id
        )

        own = Post.query.filter_by(
            user_id=user.id
        ).order_by(
            Post.created_at.desc()
        )

        pagination = followed.union(own).paginate()

        return api_success_response(
            data=[item.as_json() for item in pagination.items],
            meta=pagination.meta
        )
