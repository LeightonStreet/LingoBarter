# coding: utf-8

import logging
import re

from flask import render_template
from flask.views import MethodView


logger = logging.getLogger()


class ContentList(MethodView):
    def get(self):
        # default now, return homepage?
        return render_template("index.html")

class ChatContent(MethodView):
    def get(self):
        # frequency_map = {"a": 1}
        frequency_map = {}

        with open("/Users/Sniff/Desktop/output_1.txt", 'a') as chat_log:
            for line in chat_log:
                parts = line.split(" ")
                if parts[0].isalpha() and parts[-1].isalpha():
                    frequency_map[parts[0]] = int(parts[1])
                elif parts[0].isalpha():
                    frequency_map[parts[0][0:-1]] = int(parts[1])
                else:
                    frequency_map[parts[0][1:]] = int(parts[1])

        return render_template("wordcloud.html", frequency_map=frequency_map)


