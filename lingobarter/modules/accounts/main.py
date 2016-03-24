# coding: utf8
from lingobarter.core.app import LingobarterModule
from .views import ProfileEditView, ProfileView

module = LingobarterModule('accounts', __name__, template_folder='templates')
module.add_url_rule('/accounts/profile/<user_id>/',
                    view_func=ProfileView.as_view('profile'))
module.add_url_rule('/accounts/profile/edit/',
                    view_func=ProfileEditView.as_view('profile_edit'))
