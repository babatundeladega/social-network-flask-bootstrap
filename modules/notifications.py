from flask.views import MethodView

from .authentication import user_auth_required
from app.errors import ResourceNotFound
from app.models import Notification, User
from utils.contexts import get_current_user
from utils.response_helpers import api_success_response


class NotificationsView(MethodView):
    @user_auth_required()
    def get(self):
        current_user = get_current_user()

        pagination = Notification.query.filter(
            user_id=current_user.id
        ).paginate()

        data = []
        for item in pagination.items:
            item.mark_as_read()
            data.append(item.as_json())

        return api_success_response(
            data=data,
            meta=pagination.meta
        )
