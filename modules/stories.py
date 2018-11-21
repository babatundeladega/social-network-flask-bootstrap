from flask.views import MethodView

from .authentication import user_auth_required
from app.constants import MIN_STORY_TEXT_LENGTH
from app.errors import BadRequest, ResourceNotFound, UnauthorizedError
from app.models import Blob, Story, User
from app.models import followers
from utils.contexts import (
    get_current_request_args,
    get_current_request_data,
    get_current_user)
from utils.response_helpers import (
    api_created_response,
    api_deleted_response,
    api_success_response)
from utils.validators import check_boolean_field, check_field_length


class StoriesView(MethodView):
    @staticmethod
    def create_new_story(params):
        story = Story(
            user_id=get_current_user().id,
            **params
        )

        story.save()

        return story


    def __check_story_params(self, request_data):
        replies_enabled = request_data.get('replies_enabled')
        if replies_enabled is not None:
            check_boolean_field(replies_enabled)

        text = request_data.get('text')
        if text is not None:
            check_field_length(text, MIN_STORY_TEXT_LENGTH)

        blob_uid = request_data.get('blob_uid')
        blob = Blob.get_active(uid=blob_uid)
        if blob is None:
            raise ResourceNotFound('Blob not found')

        return dict(replies_enabled=replies_enabled, blob=blob, text=text)

    def __validate_story_creation_params(self, request_data):
        required_params = {'blob_uid'}

        missing_required_params = required_params - set(request_data.keys())
        if missing_required_params:
            raise BadRequest(
                '{} required to create a user are missing'.format(
                    required_params)
            )

        return self.__check_story_params(request_data)


    @user_auth_required()
    def get(self, story_uid=None):
        """Get a story or a list of a user's stories"""
        request_args = get_current_request_args()

        user_uid = request_args.get('user_uid')

        if user_uid is not None:
            user = User.get_active(uid=user_uid)
            if user is None:
                raise ResourceNotFound('User not found')
        else:
            user = get_current_user()

        if story_uid is not None:
            story = Story.get_active(uid=story_uid, has_expired=False)
            if story is None:
                raise ResourceNotFound('Story not found')

            return api_success_response(data=story.as_json())

        todays_stories = Story.prepare_get_active(
            user_id=user.id
        ).filter_by(
            has_expired=False
        ).all()

        return api_success_response(
            [story.as_json() for story in todays_stories])

    @user_auth_required()
    def post(self):
        """Add to a user's story"""
        request_data = get_current_request_data()

        params = self.__validate_story_creation_params(request_data)

        story = self.create_new_story(params)

        return api_created_response(story.as_json())

    @user_auth_required()
    def delete(self, story_uid):
        """Delete a slide from a user's story"""
        story = Story.get_active(uid=story_uid)
        if story is None:
            raise ResourceNotFound('Story not found')

        if story.user != get_current_user():
            raise UnauthorizedError()

        story.delete()

        return api_deleted_response()


class TimelineStoriesView(MethodView):
    @user_auth_required()
    def get(self):
        """Get the stories for a user's timeline"""
        user = get_current_user()

        followed = Story.query.join(
            followers, (followers.c.followed_id == Story.user_id)
        ).filter(
            followers.c.follower_id == user.id
        )

        own = Story.query.filter_by(user_id=user.id)

        pagination = followed.union(own).paginate()

        return api_success_response(
            data=[item.as_json() for item in pagination.items],
            meta=pagination.meta
        )
