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
        self.__APP_ID = app_id
        self.__APP_SECRET = app_secret
        self.__AK_API_Version = version
        self.__APP_Access_Token = 'AA|{}|{}'.format(
            self.__APP_ID,
            self.__APP_SECRET
        )
        self.__user_access_token = None
        self.__debug = debug
        self.__prepare_api_urls()

    def __prepare_api_urls(self):
        for k, v in self.__apis.items():
            self.__apis[k] = v.format(version=self.__AK_API_Version)

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
        Retrieve User Access Token using Authorization Code.

        :param auth_code:
        :return:
        """
        data = dict()
        params = dict(
            grant_type='authorization_code',
            code=auth_code,
            access_token=self.__APP_Access_Token
        )
        url = self.__apis.get('access_token')
        resp = requests.get(url, params=params)
        self.console_print(resp.text)
        if resp.status_code == http.HTTPStatus.OK:
            data = resp.json()
            self.__user_access_token = data.get('access_token')
        return data

    def get_app_secret_proof(self):
        """
        Generate APP secret proof using User Access Token.

        :return:
        """

        return hmac.new(
            bytes(self.__APP_SECRET, 'utf-8'),
            bytes(self.__user_access_token, 'utf-8'),
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
