from jsonschema import Draft4Validator

post_schema = {
    "type": "object",
    "properties": {
        "codigo":  {"type": "integer", "maxLength": 30},
        "name":  {"type": "string", "maxLength": 200},
    },
    "required": ["name", "codigo"],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "name":  {"type": "string", "maxLength": 200},
    },
    "additionalProperties": False
}


def validate_post_schema(json):
    return Draft4Validator(post_schema, format_checker=Draft4Validator.FORMAT_CHECKER).is_valid(json)


def validate_put_schema(json):
    return Draft4Validator(put_schema, format_checker=Draft4Validator.FORMAT_CHECKER).is_valid(json)
