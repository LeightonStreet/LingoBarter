# coding: utf-8

import os
from flask import send_from_directory, current_app, request
from flask.ext.security import roles_accepted
from lingobarter.core.views import (
    ContentList,
)


@roles_accepted('admin', 'developer')
def template_files(filename):
    template_path = os.path.join(current_app.root_path,
                                 current_app.template_folder)
    return send_from_directory(template_path, filename)


def media(filename):
    return send_from_directory(current_app.config.get('MEDIA_ROOT'), filename)


def static_from_root():
    return send_from_directory(current_app.static_folder, request.path[1:])


def configure(app):
    app.add_lingobarter_url_rule('/mediafiles/<path:filename>', view_func=media)
    app.add_lingobarter_url_rule('/template_files/<path:filename>',
                                 view_func=template_files)
    for filepath in app.config.get('MAP_STATIC_ROOT', []):
        app.add_lingobarter_url_rule(filepath, view_func=static_from_root)

    # Home page, pending more global views registration
    app.add_lingobarter_url_rule(
        '/',
        view_func=ContentList.as_view('home')
    )
