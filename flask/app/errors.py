"""Application error handlers."""
from flask import Blueprint, jsonify

errors = Blueprint("errors", __name__)


@errors.app_errorhandler(Exception)
def handle_unexpected_error(error):
    status_code = 500
    success = False
    err_message = repr(error)
    response = {
        "success": success,
        "error": {
            "type": "UnexpectedException",
            "message": "An unexpected error has occurred.",
            "error": err_message,
        },
    }

    return jsonify(response), status_code


# enable to handle errors defined in application stack
# https://opensource.com/article/17/3/python-flask-exceptions
"""
def handle_error(error):
    message = [str(x) for x in error.args]
    status_code = error.status_code
    success = False
    response = {
        'success': success,
        'error': {
            'type': error.__class__.__name__,
            'message': message
        }
    }


    return jsonify(response), status_code
"""
