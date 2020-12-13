'''Application error handlers.'''
from flask import Blueprint, jsonify

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(Exception)
def handle_unexpected_error(error):
    status_code = 500
    success = False
    response = {
        'success': success,
        'error': {
            'type': 'UnexpectedException',
            'message': 'An unexpected error has occurred.'
        }
    }

    return jsonify(response), status_code

"""    
def handle_error(error):
    message = [str(x) for x in error.args]
    #status_code = error.status_code
    success = False
    response = {
        'success': success,
        'error': {
            'type': error.__class__.__name__,
            'message': message
        }
    }

    #return jsonify(response), status_code
    return jsonify(response), status_code
"""