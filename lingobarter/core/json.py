
def render_json(message, status, **kwargs):
    ret = {
        'message': message,
        'status': status,
    }
    if kwargs is not None and len(kwargs.keys()) != 0:
        ret['response'] = kwargs
    return ret