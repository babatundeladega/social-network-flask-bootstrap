from flask.views import MethodView

from app.models import HashTag, User
from app.models import followers, hash_tag_followers
from app.errors import ResourceNotFound, ResourceConflict
from modules.authentication import user_auth_required
from utils.contexts import get_current_user
from utils.response_helpers import (
    api_created_response, api_deleted_response, api_success_response)


class UserFollowsView(MethodView):
    @user_auth_required()
    def get(self):
        """Get a list of users being followed"""
        user = get_current_user()

        pagination = user.followed.filter(
            followers.c.followed_id == user.id).paginate()

        return api_success_response(
            data=[user.as_json() for user in pagination],
            meta=pagination.meta
        )

    @user_auth_required()
    def put(self, user_uid):
        """Follow a user"""
        user = get_current_user()

        to_follow = User.get_active(uid=user_uid)
        if to_follow is None:
            raise ResourceNotFound('User not found')

        if user.is_following(to_follow):
            raise ResourceConflict('User already follows them.')

        user.followed.append(to_follow)

        return api_created_response()

    @user_auth_required()
    def delete(self, user_uid):
        """Unfollow a user"""
        user = get_current_user()

        to_unfollow = User.get_active(uid=user_uid)
        if to_unfollow is None:
            raise ResourceNotFound('User not found')

        user.followed.remove(to_unfollow)

        return api_deleted_response()


class HashTagFollowsView(MethodView):
    @user_auth_required()
    def get(self):
        """Get a list of hash tags being followed"""
        user = get_current_user()

        pagination = user.hash_tags_followed.filter(
            hash_tag_followers.c.followed_id == user.id
        ).paginate()

        return api_success_response(
            data=[user.as_json() for user in pagination],
            meta=pagination.meta
        )

    @user_auth_required()
    def put(self, hash_tag):
        """Follow a hash tag"""
        user = get_current_user()

        to_follow = HashTag.get_active(entity=hash_tag)
        if to_follow is None:
            raise ResourceNotFound('Hash tag not found')

        if user.is_following(to_follow):
            raise ResourceConflict('User already follows them.')

        user.hash_tags_followed.append(to_follow)

        return api_created_response()

    @user_auth_required()
    def delete(self, hash_tag):
        """Unfollow a hash tag"""
        user = get_current_user()

        to_unfollow = HashTag.get_active(entity=hash_tag)
        if to_unfollow is None:
            raise ResourceNotFound('Hash tag not found')

        user.hash_tags_followed.remove(to_unfollow)

        return api_deleted_response()
