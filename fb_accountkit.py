import http
import hmac
import hashlib
import requests


class FBAccountKit(object):
    """
    Facebook's AccountKit module for Server-side implementation

    https://developers.facebook.com/docs/accountkit
    """

    __apis = {
        'me': 'https://graph.accountkit.com/{version}/me',
        'access_token': 'https://graph.accountkit.com/{version}/access_token'
    }

    def __init__(self, app_id, app_secret, version='v1.1', debug=False):
        self.App_ID = app_id
        self.App_secret = app_secret
        self.API_Version = version
        self.App_Access_Token = 'AA|{}|{}'.format(
            self.App_ID,
            self.App_secret
        )
        self.__user_access_token = None
        self.__debug = debug
        self.__prepare_api_urls()

    def __prepare_api_urls(self):
        for k, v in self.__apis.items():
            self.__apis[k] = v.format(version=self.API_Version)

    def console_print(self, *args, **kwargs):
        """
        Console print for debugging.

        :param args:
        :param kwargs:
        :return:
        """
        if self.__debug:
            print(*args, **kwargs)

    def retrieve_user_access_token(self, auth_code):
        """
        Retrieve User Access Token using Authorization Code provided by Client.

        :param auth_code:
        :return:
        """
        data = dict()
        params = dict(
            grant_type='authorization_code',
            code=auth_code,
            access_token=self.App_Access_Token
        )
        url = self.__apis.get('access_token')
        resp = requests.get(url, params=params)
        self.console_print(resp.text)
        if resp.status_code == http.HTTPStatus.OK:
            data = resp.json()
            self.__user_access_token = data.get('access_token')
        return data

    def get_app_secret_proof(self, access_token=None):
        """
        Generate APP secret proof using User Access Token.

        :param access_token:
        :return:
        """
        if not access_token:
            access_token = self.__user_access_token

        return hmac.new(
            bytes(self.App_secret, 'utf-8'),
            bytes(access_token, 'utf-8'),
            hashlib.sha256
        ).hexdigest()

    def get_user_session(self):
        """
        Get user session using User Access Token

        :return:
        """

        data = dict()
        params = dict(
            access_token=self.__user_access_token,
            appsecret_proof=self.get_app_secret_proof()
        )
        url = self.__apis.get('me')
        resp = requests.get(url, params=params)
        self.console_print(resp.text)
        if resp.status_code == http.HTTPStatus.OK:
            data = resp.json()
        return data
