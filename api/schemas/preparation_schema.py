from jsonschema import Draft4Validator, draft4_format_checker

post_schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "maxLength": 250},
        "dataset":  {"type": "string", "maxLength": 200},
        "numero": {"type": "integer", "maxLength": 30},
        "preparador":   {"type": "string", "format": "email", "maxLength": 200},
        "startDate":  {"type": "string", "format": "date-time"},
        "endDate":  {"type": ["string", "null"], "format": "date-time"},
        "status":  {"type": "string", "maxLength": 50, "enum": ["Failed", "Successful"]},
        "observaciones":  {"type": ["object", "null"]},
    },
    "required": ["name", "numero", "dataset", "preparador", "startDate", "endDate", "status"],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "status":  {"type": "string", "maxLength": 50, "enum": ["Failed", "Successful"]},
        "observaciones":  {"type": ["object", "null"]},
    },
    "additionalProperties": False
}


def validate_post_schema(json):
    validator = Draft4Validator(
        post_schema, format_checker=draft4_format_checker).is_valid(json)
    return validator


def validate_put_schema(json):
    validator = Draft4Validator(
        put_schema, format_checker=draft4_format_checker).is_valid(json)
    return validator
