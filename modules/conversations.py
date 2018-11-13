from flask.views import MethodView

from .authentication import auth_required


class ConversationsView(MethodView):
    @auth_required()
    def get(self):
        pass

    @auth_required()
    def post(self):
        pass

    @auth_required()
    def delete(self, conversation_uid):
        pass
