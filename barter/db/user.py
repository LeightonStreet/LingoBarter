from barter.model import User


def fetch_all_users():
    return User.objects()


def signup_user(email, username, password):
    # check whether or not the email has been used for anther account
    u = User.objects(__raw__={'$or': [{'username': username}, {'email': email}]})
    if len(u) != 0:
        return False, "This email has been used for registration."
    User(email=email, username=username, password=password).save()
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
