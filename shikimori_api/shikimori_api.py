from typing import Callable, Mapping, Sequence, Optional, Any
import functools
import re

from requests_oauthlib import OAuth2Session


class Shikimori:
    SHIKIMORI_URL: str = 'https://shikimori.me'
    _TOKEN_URL = SHIKIMORI_URL + '/oauth/token'

    def __init__(self,
                 app_name:      Optional[str] = None,
                 *,
                 client_id:     Optional[str] = None,
                 client_secret: Optional[str] = None,
                 token:         Optional[Mapping] = None,
                 redirect_uri:  str = 'urn:ietf:wg:oauth:2.0:oob',
                 token_saver:   Optional[Callable[[dict], Any]] = None,
                 scope:         Optional[Sequence[str]] = None
                 ) -> None:

        self._client_id = client_id
        self._client_secret = client_secret
        self._token_saver = token_saver or (lambda d: None)
        self._headers = {
            'User-Agent': app_name,
        }
        self._extra = {
            'client_id': self._client_id,
            'client_secret': self._client_secret,
        }
        self._client = self._get_client(scope, redirect_uri, token)

    def _get_client(self, scope, redirect_uri, token):
        client = OAuth2Session(self._client_id, auto_refresh_url=self._TOKEN_URL, auto_refresh_kwargs=self._extra,
                               scope=scope, redirect_uri=redirect_uri, token=token, token_updater=self._token_saver)
        client.headers.update(self._headers)
        return client

    def get_auth_url(self) -> str:
        auth_url = self.SHIKIMORI_URL + '/oauth/authorize'
        return self._client.authorization_url(auth_url)[0]

    def fetch_token(self, code: str) -> dict:
        self._client.fetch_token(self._TOKEN_URL, code, client_secret=self._client_secret)
        self._token_saver(self.token)
        return self.token

    @property
    def token(self) -> dict:
        return self._client.token

    def request(self, method: str, path: str, **params):
        url = self._get_request_url(path)
        kwargs = {'params': params} if method == 'GET' else {'json': params}
        response = self._client.request(method, url, **kwargs)

        if response.ok:
            return response.json()
        response.raise_for_status()

    def _get_request_url(self, path):
        patterns = [r'/topics/\d+/ignore', r'/users/\d+/ignore', '/abuse_requests/offtopic', '/abuse_requests/summary',
                    '/abuse_requests/abuse', '/abuse_requests/spoiler', '/episode_notifications', r'/user_rates/\d+',
                    '/user_rates', r'/user_rates/\d+/increment']
        for pattern in patterns:
            if re.fullmatch(pattern, path):
                api_prefix = '/api/v2'
                break
        else:
            api_prefix = '/api'

        return self.SHIKIMORI_URL + api_prefix + path

    def get_api(self) -> 'ApiMethod':
        return ApiMethod(self)


class ApiMethod:
    _HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

    def __init__(self, session: Shikimori, path: str = '') -> None:
        self._session = session
        self._path = path

    def __call__(self, item) -> 'ApiMethod':  # item: SupportsStr
        new_path = self._path + '/' + str(item)
        return ApiMethod(self._session, new_path)

    def __getattr__(self, item) -> 'ApiMethod':
        if item in self._HTTP_METHODS:
            return functools.partial(self._session.request, item, self._path)
        new_path = self._path + '/' + item
        return ApiMethod(self._session, new_path)
