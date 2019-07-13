# fb_accountkit

A python module for server-side to integrate Facebook's AccountKit.

## Dependencies

- [requests](https://2.python-requests.org/en/master/#)

## Installation

```bash
pip install fb_accountkit
```

## Usage

```python
from fb_accountkit import FBAccountKit

fbak = FBAccountKit(
    'APP_ID',
    'APP_secret',
    version='v1.1'
)


# store token to response back to client.
token_info = fbak.retrieve_user_access_token('auth_code_from_client')

# to validate token, call `get_user_session()`
print(fbak.get_user_session())
```
