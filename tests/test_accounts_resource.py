from helper import *


def test_upload_avatar():
    res = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")
    if res['status'] == 200:
        auth = res['response']['auth_token']
        headers = {}
        if auth:
            headers['Authentication-Token'] = auth
        files = {'image': ('imgres.jpg', open('/home/lihe/Desktop/6743894.jpg', 'rb'), 'image/jpg', {'Expires': '0'})}
        r = requests.put(url_base + '/users/upload', files=files, headers=headers)
        print r.text


def test_view_profile():
    res = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")
    if res['status'] == 200:
        auth = res['response']['auth_token']
        r = get(endpoint='/users', auth=auth)
        print r


def test_log_out():
    res = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")
    if res['status'] == 200:
        auth = res['response']['auth_token']
        r = get(endpoint='/accounts/unauthorize', auth=auth)
        print r


def test_sign_up():
    print post(endpoint="/users", email="jet.in.brain@gmail.com", username="doomdagger", password="911119")


def test_username_update():
    res = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")
    if res['status'] == 200:
        auth = res['response']['auth_token']
        r = put(endpoint='/accounts/username', auth=auth, username='lingobarter-admin')
        print r


def test_password_update():
    res = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")
    if res['status'] == 200:
        auth = res['response']['auth_token']
        r = put(endpoint='/accounts/password', auth=auth, cur_password='911119', new_password='911119')
        print r


def test_password_reset():
    r = post(endpoint='/accounts/password/reset', email='jet.in.brain@gmail.com')
    print r


def test_delete_user():
    res = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")
    if res['status'] == 200:
        auth = res['response']['auth_token']
        r = delete(endpoint='/users', auth=auth)
        print r


def test_log_in():
    res = post(endpoint="/accounts/authorize", email="lingobarter.user2@gmail.com", password="user2lingobarter")
    print res


def test_view_other_profile():
    res = post(endpoint="/accounts/authorize", email="jet.in.brain@gmail.com", password="911119")
    if res['status'] == 200:
        auth = res['response']['auth_token']
        r = get(endpoint='/users/haha', auth=auth)
        print r


def test_confirmation():
    r = post(endpoint='/accounts/confirm', email='lingobarter.user2@gmail.com')
    print r

test_log_in()
