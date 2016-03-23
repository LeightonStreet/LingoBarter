# -*- coding: utf-8 -*-
import logging
logger = logging.getLogger()


def parse_conf_data(data):
    """
    @int @bool @float @json (for lists and dicts)
    strings does not need converters

    export LINGOBARTER_DEFAULT_THEME='material'
    export LINGOBARTER_DEBUG='@bool True'
    export LINGOBARTER_DEBUG_TOOLBAR_ENABLED='@bool False'
    export LINGOBARTER_PAGINATION_PER_PAGE='@int 20'
    export LINGOBARTER_MONGODB_SETTINGS='@json {"DB": "lingobarter_db", "HOST": "mongo"}'
    export LINGOBARTER_ALLOWED_EXTENSIONS='@json ["jpg", "png"]'
    :param data:
    """
    import json
    true_values = ('t', 'true', 'enabled', '1', 'on', 'yes')
    converters = {
        '@int': int,
        '@float': float,
        '@bool': lambda value: True if value.lower() in true_values else False,
        '@json': json.loads
    }
    if data.startswith(tuple(converters.keys())):
        parts = data.partition(' ')
        converter_key = parts[0]
        value = parts[-1]
        return converters.get(converter_key)(value)
    return data
