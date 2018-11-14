from flask.views import MethodView

from .authentication import user_auth_required


class StoriesView(MethodView):
    @user_auth_required()
    def get(self, user_uid):
        """Get a user's stories"""
        return

    @user_auth_required()
    def post(self, user_uid):
        """Add to a user's story"""
        return

    @user_auth_required()
    def delete(self, user_uid, slide_uid):
        """Delete a slide from a user's story"""
        return


class TimelineStoriesView(MethodView):
    @user_auth_required()
    def get(self):
        """Get the stories for a user's timeline"""
        pass
