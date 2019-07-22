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
        'access_token': 'https://graph.accountkit.com/{version}/access_token',
        'logout': 'https://graph.accountkit.com/{version}/logout',
        'invalidate_all_tokens': ' https://graph.accountkit.com/{version}/{{account_id}}/invalidate_all_tokens',
        'account_removal': 'https://graph.accountkit.com/{version}/{{account_id}}',
        'accounts': 'https://graph.accountkit.com/{version}/{app_id}/accounts/'
    }

    def __init__(self, app_id, app_secret, version='v1.1', debug=False, logger=None):
        self.App_ID = app_id
        self.App_secret = app_secret
        self.API_Version = version
        self.App_Access_Token = 'AA|{}|{}'.format(
            self.App_ID,
            self.App_secret
        )
        self.__user_access_token = None
        self.__debug = debug
        self.__logger = logger
        self.__prepare_api_urls()

    def __prepare_api_urls(self):
        """
        Prepare API urls.

        :return:
        """
        for k, v in self.__apis.items():
            self.__apis[k] = v.format(version=self.API_Version, app_id=self.App_ID)

    def __console_print(self, *args, **kwargs):
        """
        Console print for debugging.
        logger will be used if it is provided, else print() will be used instead.

        :param args:
        :param kwargs:
        :return:
        """
        if self.__debug:
            writer = print
            if self.__logger:
                writer = self.__logger.debug
            writer(*args, **kwargs)

    def retrieve_user_access_token(self, auth_code):
        """
        Retrieve User Access Token using Authorization Code provided by Client.

        REF: https://developers.facebook.com/docs/accountkit/graphapi#retrieving-user-access-tokens-with-an-authorization-code

        :param auth_code:
        :return:
        """
        params = dict(
            grant_type='authorization_code',
            code=auth_code,
            access_token=self.App_Access_Token
        )
        url = self.__apis.get('access_token')
        data = self.call_requests('get', url, params=params)
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

        REF: https://developers.facebook.com/docs/accountkit/graphapi#at-validation

        :return:
        """

        params = dict(
            access_token=self.__user_access_token,
            appsecret_proof=self.get_app_secret_proof()
        )
        url = self.__apis.get('me')
        return self.call_requests('get', url, params=params)

    def get_accounts_after_removal(self, item_per_page=100):
        """
        WARNING: USE WITH CAUTION.

        Retrieve user data after removal.

        REF: https://developers.facebook.com/docs/accountkit/graphapi#deleteapp

        :param item_per_page:
        :return:
        """

        params = dict(
            access_token=self.App_Access_Token,
            limit=item_per_page
        )
        url = self.__apis.get('accounts')
        return self.call_requests('get', url, params=params)

    def logout(self):
        """
        WARNING: USE WITH CAUTION.

        Logout session of the user.

        REF: https://developers.facebook.com/docs/accountkit/graphapi#logout

        :return:
        """
        params = dict(
            access_token=self.__user_access_token,
            appsecret_proof=self.get_app_secret_proof(self.__user_access_token)
        )
        url = self.__apis.get('logout')
        return self.call_requests('post', url, params=params)

    def logout_all_session(self, account_id):
        """
        WARNING: USE WITH CAUTION.

        Logout all sessions of given account_id.

        REF: https://developers.facebook.com/docs/accountkit/graphapi#logout

        :param account_id:
        :return:
        """
        url = self.__apis.get('invalidate_all_tokens').format(account_id=account_id)
        params = dict(
            access_token=self.App_Access_Token
        )
        return self.call_requests('post', url, params=params)

    def remove(self, account_id):
        """
        WARNING: USE WITH CAUTION.

        Delete an account from the database stored on Account Kit servers.

        :param account_id:
        :return:
        """
        url = self.__apis.get('account_removal').format(account_id=account_id)
        params = dict(
            access_token=self.App_Access_Token
        )
        return self.call_requests('delete', url, params=params)

    def call_requests(self, method, url, *args, **kwargs):
        """
        A wrapper function for python-requests.
        Raise if requests.exceptions.HTTPError occurred.

        :param method:
        :param url:
        :param args:
        :param kwargs:
        :return:
        """
        format_http_request = '{http_method} {status_code} {url}'
        format_func_params = '{arg_type} {args}'
        if args:
            self.__console_print(format_func_params.format(arg_type='ARGS', args=args))
        if kwargs:
            self.__console_print(format_func_params.format(arg_type='KWARGS', args=kwargs))
        http_method = getattr(requests, method)
        resp = http_method(url, *args, **kwargs)
        self.__console_print(
            format_http_request.format(
                http_method=method.upper(),
                url=url,
                status_code=resp.status_code))
        self.__console_print(resp.text)
        resp.raise_for_status()
        return resp.json()
