from barter.model import User


def fetch_all_users():
    return User.objects()


def signup_user(email, username, password):
    # check whether or not the email has been used for anther account
    u = User.objects(__raw__={'$or': [{'username': username}, {'email': email}]})
    if len(u) != 0:
        return False, "This email has been used for registration."
    u = User(email=email, username=username, password=password)
    u.save()
    u.profile_completed = False
    return True, None


# log in
def fetch_user(email, password):
    u = User.objects(email=email, password=password)
    if len(u) == 0:
        return None
    else:
        return u[0]


def logout_user():
    pass


# complete user profile
# user has already logged in
# username, nickname, nationality, location, sex, age, introduction, teach_lan, learn_lan
def update_user(**kwargs)
    u = User.objects(email=kwargs['username'])[0]

    u.nickname = kwargs['nickname']
    u.nationality = kwargs['nationality']
    u.location = kwargs['location']
    u.sex = kwargs['sex']
    u.age = kwargs['age']
    u.introduction = kwargs['introduction']
    u.teach_lan = kwargs['teach_lan']
    u.learn_lan = kwargs['learn_lan']
    u.profile_completed = True
    u.save()

