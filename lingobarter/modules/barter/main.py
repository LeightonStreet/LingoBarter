# coding: utf8
from lingobarter.core.app import LingobarterModule
from lingobarter.core.api import LingobarterApi

# create our module based on blueprint
module = LingobarterModule('barter', __name__, template_folder='templates')
# create our api service based on this module, default prefix will be /api/v1/
api_v1 = LingobarterApi(module, version='v1')
