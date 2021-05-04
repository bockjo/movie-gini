import json
from flask import request, _request_ctx_stack
from flask import Flask, request, jsonify, abort
from functools import wraps
from jose import jwt
from urllib.request import urlopen

from config import auth0_config

#Login URI
"""
https://johannes-udacity.us.auth0.com/authorize?audience=gini&response_type=token&client_id=K1cunY0C7g6Ew9V4T7iCLLlJxOXM9RPZ&redirect_uri=http://127.0.0.1:5000/login-results
"""

AUTH0_DOMAIN = auth0_config["AUTH0_DOMAIN"]
ALGORITHMS = auth0_config["ALGORITHMS"]
API_AUDIENCE = auth0_config["API_AUDIENCE"]



# AuthError Exception
class AuthError(Exception):
    """
    AuthError Exception
    A standardized way to communicate auth failure modes
    """

    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header
def get_token_auth_header():
    auth_header = request.headers.get("Authorization", None)

    if auth_header is None:
        raise AuthError({
            "success":False,
            "error":401,
            "code": "authorization_header_missing",
            "message": "Authorization Header is required."
        }, 401)

    auth_header_values = auth_header.split(" ")
    if len(auth_header_values) != 2:
        raise AuthError({
            "success":False,
            "error":401,
            "code": "invalid_authorization_header",
            "message": "Authorization Header is malformed."
        }, 401)
    elif auth_header_values[0].lower() != "bearer":
        raise AuthError({
            "success":False,
            "error":401,
            "code": "invalid_authorization_header",
            "message": "Authorization Header must start with \"Bearer\"."
        }, 401)

    return auth_header_values[1]


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            "success":False,
            "error":400,
            'code': 'invalid_claims',
            'message': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            "success":False,
            "error":403,
            'code': 'unauthorized',
            'message': 'Requested Permission not found.'
        }, 403)

    return True


def verify_decode_jwt(token):
    url_string = "https://{}/.well-known/jwks.json".format(AUTH0_DOMAIN)
    json_url = urlopen(url_string)
    jwks = json.loads(json_url.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}

    if 'kid' not in unverified_header:
        raise AuthError({
            "success":False,
            "error":401,
            'code': 'invalid_authorization_header',
            'message': 'Authorization Header is malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }

    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://{}/'.format(AUTH0_DOMAIN)
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                "success":False,
                "error":401,
                'code': 'token_expired',
                'message': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                "success":False,
                "error":401,
                'code': 'invalid_claims',
                'message':
                    'Incorrect claims. Please check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                "success":False,
                "error":401,
                'code': 'invalid_authorization_header',
                'message': 'Unable to parse authentication token.'
            }, 401)

    raise AuthError({
        "success":False,
        "error":401,
        'code': 'invalid_authorization_header',
        'message': 'Unable to find the appropriate key.'
    }, 401)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                token = get_token_auth_header()
                payload = verify_decode_jwt(token)
                check_permissions(permission, payload)
            except AuthError as authError:
                raise abort(authError.status_code,
                            authError.error["message"])

            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator