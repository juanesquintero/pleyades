from jsonschema import Draft4Validator, draft4_format_checker

nombre_schema = {
    "type": "object",
    "properties": {
        "program":  {"type": "integer", "maxLength": 30},
        "manager":   {"type": "string", "format": "email", "maxLength": 200},
        "tipo":  {"type": "string", "maxLength": 50},
        "initialPeriod":  {"type": "integer", "maxLength": 6},
        "finalPeriod":  {"type": "integer", "maxLength": 6},
        "status":  {"type": "string", "maxLength": 50},
    },
    "required": ["program", "manager", "tipo", "initialPeriod", "finalPeriod", "status"],
    "additionalProperties": False
}

post_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "maxLength": 200},
        "numero": {"type": "integer", "maxLength": 30},
        "program":  {"type": "integer", "maxLength": 30},
        "manager":   {"type": "string", "format": "email", "maxLength": 200},
        "tipo":  {"type": "string", "maxLength": 50},
        "initialPeriod":  {"type": "integer", "maxLength": 6},
        "finalPeriod":  {"type": "integer", "maxLength": 6},
        "status":  {"type": "string", "maxLength": 50},
    },
    "required": ["name", "program", "manager", "tipo", "initialPeriod", "finalPeriod", "status"],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "manager":   {"type": "string", "format": "email", "maxLength": 200},
        "status":  {"type": "string", "maxLength": 50},
    },
    "additionalProperties": False
}


def validate_nombre_schema(json):
    return Draft4Validator(nombre_schema, format_checker=draft4_format_checker).is_valid(json)


def validate_post_schema(json):
    return Draft4Validator(post_schema, format_checker=draft4_format_checker).is_valid(json)


def validate_put_schema(json):
    return Draft4Validator(put_schema, format_checker=draft4_format_checker).is_valid(json)
