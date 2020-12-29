from flask import session, redirect
from functools import wraps
import os


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('profile', None)
        # You would add a check here and use the user id or something to fetch
        # the other data for that user/check if they exist
        if user:
            return f(*args, **kwargs)
        return redirect('/')

    return decorated_function


def is_valid_user(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = dict(session).get('profile', None)
        validEmails = os.environ.get('VALID_EMAILS')
        validEmailList = [x.strip() for x in validEmails.lstrip(',').rstrip(',').split(',')]
        # print('is_valid_user {}'.format(user))
        if user is not None:
            if user['email'] in validEmailList:
                return f(*args, **kwargs)
        return redirect('/')

    return decorated_function
