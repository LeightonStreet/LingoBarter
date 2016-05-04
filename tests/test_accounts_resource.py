import requests
import json

url_base = "http://localhost:8080/api/v1"


def post(endpoint, auth=None, **kwargs):
    headers = {'content-type': 'application/json'}
    if auth:
        headers['Authentication-Token'] = auth
    payload = json.dumps(kwargs)
    r = requests.post(url_base + endpoint, data=payload, headers=headers)
    return r.json()


def get(endpoint, auth=None):
    headers = {}
    if auth:
        headers['Authentication-Token'] = auth
    r = requests.get(url_base + endpoint, headers=headers)
    return r.json()


print post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="ll1222")
