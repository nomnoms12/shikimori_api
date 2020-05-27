# shikimori_api
[![Build Status](https://travis-ci.com/nomnoms12/shikimori_api.svg?branch=master)](https://travis-ci.com/nomnoms12/shikimori_api)
[![Coverage Status](https://coveralls.io/repos/github/nomnoms12/shikimori_api/badge.svg?branch=master)](https://coveralls.io/github/nomnoms12/shikimori_api?branch=master)
[![License](https://img.shields.io/github/license/nomnoms12/shikimori_api?color=blueviolet)](https://github.com/nomnoms12/shikimori_api/blob/master/LICENSE)
[![Shikimori Status](https://img.shields.io/website?url=https%3A%2F%2Fshikimori.one)](https://shikimori.one)

Unofficial wrapper for the [Shikimori API](https://shikimori.one/api/doc)

# Installation
This package requires Python 3.6 or later
```
pip install shikimori_api
```

## Dependencies
 - [requests-oauthlib](https://github.com/requests/requests-oauthlib)

# Usage
```python
from shikimori_api import Shikimori


session = Shikimori()
api = session.get_api()

api.animes.GET(search='KonoSuba', kind='movie')  # GET /api/animes?search=KonoSuba&kind=movie
api.animes(1).GET()                              # GET /api/animes/1
api.animes(1).screenshots.GET()                  # GET /api/animes/1/screenshots
```

## OAuth
```python
import json


def token_saver(token: dict):
    with open('token.json', 'w') as f:
        f.write(json.dumps(token))


session = Shikimori('APP_NAME', client_id='CLIENT_ID', client_secret='CLIENT_SECRET', token_saver=token_saver)

print(session.get_auth_url())
code = input('Authorization Code: ')
session.fetch_token(code)
```
After receiving and saving token, you can load it from file:
```python
with open('token.json') as f:
    token = json.load(f)
session = Shikimori('APP_NAME', client_id='CLIENT_ID', client_secret='CLIENT_SECRET',
                    token=token, token_saver=token_saver)
```
