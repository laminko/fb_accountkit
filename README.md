# fb_accountkit

A simple python module for Facebook's [AccountKit](https://developers.facebook.com/docs/accountkit/) server-side implementations.

## Dependencies

- [requests](https://2.python-requests.org/en/master/#)

## Installation

```bash
pip install fb-accountkit
```

## Usage

```python
from fb_accountkit import FBAccountKit

fbak = FBAccountKit(
    'APP_ID',
    'APP_secret',
    version='v1.1'
)

# store token (user_access_token) to response back to client.
token_info = fbak.retrieve_user_access_token('auth_code_from_client')

# to validate token, call `get_user_session()`
print(fbak.get_user_session())

# to logout the user
fbak.logout()

# to logout all sessions (account_id must be provided)
me = fbak.get_user_session()
fbak.logout_all_session(me.get('id'))

```
