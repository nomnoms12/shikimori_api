import json

import pytest
import responses
from requests.exceptions import HTTPError

from shikimori_api import Shikimori
from shikimori_api.shikimori_api import ApiMethod


SHIKIMORI_URL = 'https://shikimori.one'
TOKEN_URL = SHIKIMORI_URL + '/oauth/token'


@pytest.fixture
def mocked_responses():
    with responses.RequestsMock() as rsps:
        yield rsps


def test_token(mocked_responses):
    token = {'access_token': 'bar'}

    def request_callback(request):
        assert request.headers['User-Agent'] == 'Api Test'
        return 100, {}, json.dumps(token)
    mocked_responses.add_callback(responses.POST, TOKEN_URL, callback=request_callback)

    def token_saver(d):
        assert d == token

    s = Shikimori('Api Test', token_saver=token_saver)

    assert s.fetch_token('foo') == token
    assert s.token == token


def test_request_headers(mocked_responses):
    def request_callback(request):
        assert request.headers['User-Agent'] == 'Api Test'
        return 100, {}, json.dumps([])
    url = SHIKIMORI_URL + '/api'
    mocked_responses.add_callback(responses.GET, url, callback=request_callback)

    s = Shikimori('Api Test')
    s.request('GET', '')


def test_http_code_is_not_ok(mocked_responses):
    def request_callback(_):
        return 404, {}, ''
    url = SHIKIMORI_URL + '/api'
    mocked_responses.add_callback(responses.GET, url, callback=request_callback)

    s = Shikimori()
    with pytest.raises(HTTPError):
        s.request('GET', '')


def test_get_api():
    s = Shikimori()
    api = s.get_api()

    assert type(api) == ApiMethod
    assert api._session == s


def test_get_auth_url():
    s = Shikimori()
    auth_url = s.get_auth_url()

    assert auth_url.startswith(SHIKIMORI_URL + '/oauth/authorize?')


def test_get_request_uri():
    s = Shikimori()

    assert s._get_request_url('/some_method') == SHIKIMORI_URL + '/api/some_method'

    assert s._get_request_url('/topics/12/ignore') == SHIKIMORI_URL + '/api/v2/topics/12/ignore'
    assert s._get_request_url('/users/12/ignore') == SHIKIMORI_URL + '/api/v2/users/12/ignore'
    assert s._get_request_url('/users/12/ignore') == SHIKIMORI_URL + '/api/v2/users/12/ignore'
    assert s._get_request_url('/abuse_requests/offtopic') == SHIKIMORI_URL + '/api/v2/abuse_requests/offtopic'
    assert s._get_request_url('/abuse_requests/summary') == SHIKIMORI_URL + '/api/v2/abuse_requests/summary'
    assert s._get_request_url('/abuse_requests/abuse') == SHIKIMORI_URL + '/api/v2/abuse_requests/abuse'
    assert s._get_request_url('/abuse_requests/spoiler') == SHIKIMORI_URL + '/api/v2/abuse_requests/spoiler'
    assert s._get_request_url('/episode_notifications') == SHIKIMORI_URL + '/api/v2/episode_notifications'
    assert s._get_request_url('/user_rates/12') == SHIKIMORI_URL + '/api/v2/user_rates/12'
    assert s._get_request_url('/user_rates') == SHIKIMORI_URL + '/api/v2/user_rates'
    assert s._get_request_url('/user_rates/12/increment') == SHIKIMORI_URL + '/api/v2/user_rates/12/increment'


def test_api_method_class():
    s = Shikimori()
    api = s.get_api()

    assert type(api.some_method) is ApiMethod
    assert type(api(12)) is ApiMethod

    assert getattr(api.some_method, '_path') == '/some_method'
    assert getattr(api.some_method.sub_method, '_path') == '/some_method/sub_method'
    assert getattr(api(12), '_path') == '/12'
    assert getattr(api(12)(3730), '_path') == '/12/3730'
    assert getattr(api.some_method(12), '_path') == '/some_method/12'
    assert getattr(api.some_method(12).sub_method(3730), '_path') == '/some_method/12/sub_method/3730'

    method = api.some_method
    partial = method.GET

    assert getattr(partial, 'func') == s.request
    assert getattr(partial, 'args') == ('GET', method._path)
    assert getattr(partial, 'keywords') == {}

    partial = method.POST

    assert getattr(partial, 'args') == ('POST', method._path)
