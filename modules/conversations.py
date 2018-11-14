from flask.views import MethodView

from .authentication import user_auth_required


class ConversationsView(MethodView):
    @user_auth_required()
    def get(self):
        pass

    @user_auth_required()
    def post(self):
        pass

    @user_auth_required()
    def delete(self, conversation_uid):
        pass
