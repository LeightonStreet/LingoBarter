# coding: utf8
from lingobarter.core.app import LingobarterModule
from lingobarter.core.api import LingobarterApi
from .views import ProfileEditView, ProfileView
from .resouces import (LoginResource, LogoutResource, UserViewResource,
                       UserResource, UploadAvatar, PasswordResource,
                       PasswordResetResource, UsernameResource, ConfirmationRequestResource)

# create our module based on blueprint
module = LingobarterModule('accounts', __name__, template_folder='templates')
# create our api service based on this module, default prefix will be /api/v1/
api_v1 = LingobarterApi(module, version='v1')

# add normal url routing
module.add_url_rule('/accounts/profile/<user_id>/',
                    view_func=ProfileView.as_view('profile'))
module.add_url_rule('/accounts/profile/edit/',
                    view_func=ProfileEditView.as_view('profile_edit'))

# add restful webservice endpoints
api_v1.add_lingobarter_resource(LoginResource, '/accounts/authorize')
api_v1.add_lingobarter_resource(LogoutResource, '/accounts/unauthorize')
api_v1.add_lingobarter_resource(UserResource, '/users')
api_v1.add_lingobarter_resource(UserViewResource, '/users/<username>')
api_v1.add_lingobarter_resource(UploadAvatar, '/users/upload')

api_v1.add_lingobarter_resource(PasswordResource, '/accounts/password')
api_v1.add_lingobarter_resource(PasswordResetResource, '/accounts/password/reset')
api_v1.add_lingobarter_resource(UsernameResource, '/accounts/username')
api_v1.add_lingobarter_resource(ConfirmationRequestResource, '/accounts/confirm')
