from barter.model import User


def fetch_all_users():
    return User.objects()


def signup_user(email, username, password):
    # check whether or not the email has been used for anther account
    for u in fetch_all_users():
        if u.email == email:
            return False, "This email has been used for registration."
    User(email=email, username=username, password=password).save()
    return True


# log in
def fetch_user(email, password):
    user_exist = False
    for u in fetch_all_users():
        if email == u.email:
            user_exist = True
            # check password
            if password == u.password:
                return True
            else:
                return False, "Wrong password."
    if not user_exist:
        return False, "User does not exist."


def logout_user():
    pass
