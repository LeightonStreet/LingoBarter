# coding: utf-8

from flask_restful import Resource
from lingobarter.core.json import render_json
from lingobarter.modules.accounts.models import Language


class LanguageResource(Resource):
    def get(self):
        languages = {}

        for lang in Language.objects:
            languages[lang.name] = {
                'id': str(lang.id),
                "name": lang.name,
                "u_name": lang.u_name,
                "abbrev": lang.abbrev
            }

        return render_json(message="Successfully fetch all languages", status=200, **languages)
