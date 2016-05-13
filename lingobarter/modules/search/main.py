# coding: utf8
from lingobarter.core.app import LingobarterModule
from lingobarter.core.api import LingobarterApi
from .resources import SearchResource, ContentResource

# create our module based on blueprint
module = LingobarterModule('search', __name__, template_folder='templates')
# create our api service based on this module, default prefix will be /api/v1/
api_v1 = LingobarterApi(module, version='v1')

# add restful webservice endpoints
api_v1.add_lingobarter_resource(SearchResource, '/search')
api_v1.add_lingobarter_resource(ContentResource, '/content')
