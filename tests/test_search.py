from helper import *

# log in
auth = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")['response']['auth_token']

search_conditions = {
    'age_range': [0, 100],
    'nationality': ['China', 'USA'],
    'teach_langs': [
        {
            'language_id': 'English'
        },
        {
            'language_id': 'Italian',
            'level': 5
        }
    ],
    'learn_langs': [
        {
            'language_id': 'Chinese Simplified',
            'level': [1, 3]
        },
        {
            'language_id': 'German'
        }
    ],
    'has_bio': False,
    'page_id': 0,  # default 0, counting from 0
    'page_size': 30  # default 20
}

post(endpoint="/search", auth=auth, **search_conditions)