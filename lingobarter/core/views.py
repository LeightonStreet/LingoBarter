# coding: utf-8

import logging

from flask import render_template
from flask.views import MethodView

logger = logging.getLogger()


class ContentList(MethodView):
    def get(self):
        # default now, return homepage?
        return render_template("index.html")
