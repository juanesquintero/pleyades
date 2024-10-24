from jsonschema import Draft4Validator, draft4_format_checker

post_schema = {
    'type': 'object',
    'properties': {
        'nombre': {'type': 'string', 'maxLength': 250},
        'set':  {'type': 'string', 'maxLength': 200},
        'numero': {'type': 'integer', 'maxLength': 30},
        'ejecutor':   {'type': 'string', 'format': 'email', 'maxLength': 200},
        'fechaInicial':  {'type': 'string', 'format': 'date-time'},
        'fechaFinal':  {'type': ['string', 'null'], 'format': 'date-time'},
        'estado':  {'type': 'string', 'maxLength': 50, 'enum': ['Fallida', 'Exitosa']},
        'precision_model': {'type': ['number', 'null'], 'maxLength': 5},
        'results':  {'type': 'object'},
    },
    'required': ['nombre', 'set', 'numero', 'ejecutor', 'fechaInicial', 'fechaFinal', 'estado', 'results'],
    'additionalProperties': False
}

put_schema = {
    'type': 'object',
    'minProperties': 1,
    'properties': {
        'results':  {'type': 'object'},
        'estado':  {'type': 'string', 'maxLength': 50, 'enum': ['Fallida', 'Exitosa']},
    },
    'additionalProperties': False
}


def validate_post_schema(json):
    validator = Draft4Validator(
        post_schema, format_checker=draft4_format_checker).is_valid(json)
    return validator


def validate_put_schema(json):
    validator = Draft4Validator(
        put_schema, format_checker=draft4_format_checker).is_valid(json)
    return validator
