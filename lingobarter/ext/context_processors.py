# coding: utf-8

from lingobarter.core.models.config import Config


def configure(app):

    @app.context_processor
    def inject():
        return dict(
            Config=Config,
        )
