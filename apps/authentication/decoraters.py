from functools import wraps
from flask import jsonify

from flask_jwt_extended import get_jwt, verify_jwt_in_request

# Decorater for role check
def role_check(role):
    def inner_role_check(function):
        @wraps(function)
        def decorator(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            if ("role" in claims) and (role in claims["role"]):
                return function(*args,** kwargs)
            else:
                return jsonify(msg="Missing Authorization Header"), 401
        return decorator
    return inner_role_check