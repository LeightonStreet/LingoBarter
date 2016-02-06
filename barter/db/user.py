from barter.model import User


def fetch_all_users():
    return User.objects()


def signup_user(email, username, password):
    User(email=email, username=username, password=password).save()
    return True
