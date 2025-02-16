from jsonschema import Draft4Validator

from api.utils.constants import Roles

post_schema = {
    'type': 'object',
    'properties': {
        'name': {'type': 'string', 'maxLength': 250},
        'dataset':  {'type': 'string', 'maxLength': 200},
        'number': {'type': 'integer', 'maxLength': 30},
        Roles.EXECUTOR:   {'type': 'string', 'format': 'email', 'maxLength': 200},
        'startDate':  {'type': 'string', 'format': 'date-time'},
        'endDate':  {'type': ['string', 'null'], 'format': 'date-time'},
        'status':  {'type': 'string', 'maxLength': 50, 'enum': ['Failed', 'Successful']},
        'model_accuracy': {'type': ['number', 'null'], 'maxLength': 5},
        'results':  {'type': 'object'},
    },
    'required': ['name', 'dataset', 'number', Roles.EXECUTOR, 'startDate', 'endDate', 'status', 'results'],
    'additionalProperties': False
}

put_schema = {
    'type': 'object',
    'minProperties': 1,
    'properties': {
        'results':  {'type': 'object'},
        'status':  {'type': 'string', 'maxLength': 50, 'enum': ['Failed', 'Successful']},
    },
    'additionalProperties': False
}


def validate_post_schema(json):
    validator = Draft4Validator(
        post_schema, format_checker=Draft4Validator.FORMAT_CHECKER).is_valid(json)
    return validator


def validate_put_schema(json):
    validator = Draft4Validator(
        put_schema, format_checker=Draft4Validator.FORMAT_CHECKER).is_valid(json)
    return validator
