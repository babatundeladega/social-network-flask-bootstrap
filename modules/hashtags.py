from flask.views import MethodView

from app.constants import (
    DEFAULT_HASH_TAG_FETCH_SCOPE, HASH_TAG_RETRIEVAL_SCOPES)
from app.errors import BadRequest, ResourceNotFound
from app.models import HashTag
from utils.contexts import get_current_request_args
from utils.response_helpers import api_success_response


class HashTagsView(MethodView):
    @staticmethod
    def create_hash_tag(entity):
        hash_tag = HashTag(entity=entity)
        hash_tag.save()

        return hash_tag

    @staticmethod
    def add_post_to_hash_tag(post, hash_tag):
        post.hash_tags.append(hash_tag)


    def get(self, hash_tag):
        """Retrieve posts about an hashtag"""
        request_args = get_current_request_args()

        scope = request_args.get('scope') or DEFAULT_HASH_TAG_FETCH_SCOPE
        if scope not in HASH_TAG_RETRIEVAL_SCOPES:
            raise BadRequest(
                '`scope` must be one of {}'.format(HASH_TAG_RETRIEVAL_SCOPES))

        hash_tag = HashTag.get_not_deleted(hash_tag=hash_tag)
        if hash_tag is None:
            raise ResourceNotFound('Hash tag not found')

        hash_tag_details = {
            'meta': lambda x: {
                'data': None,
                'meta': None
            },
            'posts': lambda y: {
                'data': None,
                'meta': None
            },
            'followers': lambda z: {
                'data': None,
                'meta': None
            }
        }

        scoped_details = hash_tag_details[scope]()

        return api_success_response(**scoped_details)
