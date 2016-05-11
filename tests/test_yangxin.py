from helper import *
import datetime
from lingobarter.utils import dateformat

# sign up
# print post(endpoint="/users", username="Xin", email="coco.xin.yang2013@gmail.com", password="111111")
# print post(endpoint="/users", username="Coco", email="coco.xin.yang2015@gmail.com", password="222222")


# log in
# auth = post(endpoint="/accounts/authorize", email="coco.xin.yang2013@gmail.com", password="111111")['response']['auth_token']
auth = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")['response']['auth_token']
# print get(endpoint="/users", auth=auth)
# print get(endpoint="/users/Coco", auth=auth)

new_profile = {
    'bio': 'new bio',
    'teach_langs': [
        {
            'language_id': 'CN',
            'level': 4
        },
        {
            'language_id': 'IT',
            'level': 5
        },
        {
            'language_id': 'CA',
            'level': 4
        }
    ],
    'learn_langs': [
        {
            'language_id': 'EN',
            'level': 1
        }, {
            'language_id': 'FR',
            'level': 2
        }
    ],
    'birthday': dateformat.datetime_to_timestamp(datetime.datetime(2012, 06, 29)),
    'gender': 'female',
    'nationality': 'China',
    'settings': {
        'hide_from_search': False,
        'same_gender': False,
        'age_range': [2, 4],
        'strict_lang_match': True
    }
}

# print json.dumps(new_profile, indent=True)

put(endpoint="/users", auth=auth, **new_profile)

# get(endpoint='/users/Coco', auth=auth)

get(endpoint='/accounts/unauthorize', auth=auth)
