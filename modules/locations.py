from flask.views import MethodView
from geopy.geocoders import Nominatim

from .authentication import user_auth_required
from app.constants import MIN_LOCATION_NAME_LENGTH
from app.errors import BadRequest, ResourceNotFound
from app.models import Location
from utils.contexts import get_current_request_data
from utils.validators import check_coordinate_field, check_field_length


class LocationsView(MethodView):
    @staticmethod
    def create_location(params):
        geo_locator = Nominatim()

        geo_location = geo_locator.reverse(
            "{}, {}".format(params['longitude'], params['latitude'])
        ).raw

        geo_location_details = {
            'city': geo_location['address']['suburb'],
            'state_or_province': geo_location['address']['state'],
            'country': geo_location['address']['country'],
            'postal_code': geo_location['address']['postcode'],
            'street_address': geo_location
        }

        params.update(geo_location_details)

        location = Location(
            **params
        )

        location.save()

        return location

    @staticmethod
    def edit_location(location, params):
        location.update(**params)

        return location


    def __check_locations_params(self, request_data):
        latitude = request_data.get('latitude')
        if latitude is not None:
            check_coordinate_field(latitude)

        longitude = request_data.get('longitude')
        if longitude is not None:
            check_coordinate_field(longitude)

        name = request_data.get('name')
        if name is not None:
            check_field_length(name, MIN_LOCATION_NAME_LENGTH)

        return dict(
            latitude=latitude,
            longitude=longitude,
            name=name
        )

    def __validate_location_creation_params(self, request_data):
        required_params = {'longitude', 'latitude'}
        missing_required_params = required_params - set(request_data.keys())
        if missing_required_params:
            raise BadRequest('{} are missing.'.format(missing_required_params))

        return self.__check_locations_params(request_data)

    def __validate_location_update_params(self, request_data):
        return self.__check_locations_params(request_data)


    @user_auth_required()
    def get(self, location_uid):
        location = Location.get_active(uid=location_uid)
        if location is None:
            raise ResourceNotFound('Location not found')

        return location.as_json()

    @user_auth_required()
    def post(self):
        request_data = get_current_request_data()

        params = self.__validate_location_creation_params(request_data)

        location = self.create_location(params)

        return location.as_json()

    @user_auth_required()
    def patch(self, location_uid):
        request_data = get_current_request_data()

        location = Location.get_active(uid=location_uid)
        if location is None:
            raise ResourceNotFound('Location not found')

        params = self.__validate_location_update_params(request_data)

        location = self.edit_location(location, params)

        return location.as_json()
