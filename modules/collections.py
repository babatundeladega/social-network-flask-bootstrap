from flask.views import MethodView

from .authentication import user_auth_required
from app.constants import MIN_COLLECTION_NAME_LENGTH
from app.errors import BadRequest, ResourceNotFound
from app.models import Collection, Post, User
from utils.contexts import (
    get_current_request_args,
    get_current_request_data,
    get_current_user)
from utils.response_helpers import (
    api_created_response,
    api_deleted_response,
    api_success_response)
from utils.validators import check_field_length


class CollectionsView(MethodView):
    @staticmethod
    def create_collection(params):
        """Create a collection and return the ORM object of the collection
        created"""
        collection = Collection(**params)
        collection.save()

        return collection

    @staticmethod
    def edit_collection(collection, params):
        """Edit a collection and return the ORM object of the collection
        edited"""
        collection.update(params)

        return collection


    def __check_collections_params(self, request_data):
        name = request_data.get('name')

        if name is not None:
            check_field_length(name, MIN_COLLECTION_NAME_LENGTH)

        return dict(
            name=name
        )

    def __validate_collection_creation_params(self, request_data):
        required_params = {'name'}

        missing_required_params = required_params - set(request_data.keys())
        if missing_required_params:
            raise BadRequest(
                'Missing required params: {}'.format(missing_required_params))

        return self.__check_collections_params(request_data)

    def __validate_collection_update_params(self, request_data):
        return self.__check_collections_params(request_data)
    
    
    @user_auth_required()
    def post(self):
        """Create a collection"""
        request_data = get_current_request_data()

        params = self.__validate_collection_creation_params(request_data)

        collection = self.create_collection(params)

        return api_created_response(collection.as_json())

    @user_auth_required()
    def get(self, collection_uid=None):
        """Get a list of a user's collections, or """
        request_args = get_current_request_args()

        user_uid = request_args.get('user_uid')

        if user_uid is not None:
            user = User.get_not_deleted(uid=user_uid)
            if user is None:
                raise ResourceNotFound('User not found')

        else:
            user = get_current_user()

        if collection_uid is not None:
            collection = Collection.get_not_deleted(
                uid=collection_uid,
                user_id=user.id
            )

            if collection is None:
                raise ResourceNotFound('Collection not found')

            return api_success_response(collection.as_json())

        pagination = user.collections.paginate()

        return api_success_response(
            data=[collection.as_json() for collection in pagination.items()],
            meta=pagination.meta
        )

    def patch(self, collection_uid):
        request_data = get_current_request_data()

        collection = Collection.get_active(collection_uid)
        if collection is None:
            raise ResourceNotFound('Collection not found')

        params = self.__validate_collection_update_params(request_data)

        collection = self.edit_collection(collection, params)

        return api_success_response(collection.as_json())

    def delete(self, collection_uid):
        """Delete a collection"""
        collection = Collection.get_active(collection_uid)
        if collection is None:
            raise ResourceNotFound('Collection not found')

        collection.delete()

        return api_deleted_response()


class CollectionPostsView(MethodView):
    def put(self, collection_uid, post_uid):
        """Add a post to a collection"""
        collection = Collection.get_not_deleted(uid=collection_uid)
        if collection is None:
            raise ResourceNotFound('Collection not found')

        post = Post.get_not_deleted(uid=post_uid)
        if post is None:
            raise ResourceNotFound('Post not found')

        post.update(collection_id=collection.id)

        return api_success_response()

    def delete(self, collection_uid, post_uid):
        """Remove a post from a collection"""
        collection = Collection.get_not_deleted(uid=collection_uid)
        if collection is None:
            raise ResourceNotFound('Collection not found')

        post = Post.get_not_deleted(uid=post_uid)
        if post is None:
            raise ResourceNotFound('Post not found')

        if post.collection_id != collection.id:
            raise ResourceNotFound('Post not found')

        post.update(collection_id=None)

        return api_deleted_response()
