from service import db
# Codacy lies, this is used.
from service.api.extensions import guard
from service.api.models import User

import json
from datetime import date
from datetime import datetime


class JsonExtendEncoder(json.JSONEncoder):
    """
        This class provide an extension to json serialization for datetime/date.
    """
    def default(self, o):
        """
            provide a interface for datetime/date
        """
        if isinstance(o, datetime):
            return o.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(o, date):
            return o.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, o)


def convert_timestamp(item_date_object):
    if isinstance(item_date_object, (date, datetime)):
        return item_date_object.timestamp()


def add_user(username, email, password, roles=None):
    baseline = {'username': username, 'email': email, 'password': password}
    user = User(**baseline)
    if roles:
        user.roles = roles
    db.session.add(user)
    db.session.commit()
    return user


def get_user_token(client, email, password):
    return login_user(client, email, password)['auth_token']


def login_user(client, email, password):
    login = client.post(
        '/api/auth/login',
        data=json.dumps({
            'email': email,
            'password': password,
            }),
        content_type='application/json',
        )
    return json.loads(login.data.decode())


def get_url_with_token(client, url, token):
    response = client.get(
        url,
        content_type='application/json',
        headers={'Authorization': f'Bearer {token}'}
        )
    return response
