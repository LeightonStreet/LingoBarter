# coding: utf-8

import logging
from flask import current_app

from flask import render_template
from flask.views import MethodView


logger = logging.getLogger()


class ContentList(MethodView):
    def get(self):
        # default now, return homepage?
        return render_template("index.html")


class ChatContent(MethodView):
    def get(self):
        frequency_map = {}

        with open(current_app.config['MAP_REDUCE_FILE'], 'r') as chat_log:
            for line in chat_log:
                parts = line.split(" ")
                frequency_map[str(parts[0])] = int(parts[1])

        return render_template("wordcloud.html", frequency_map=frequency_map)
