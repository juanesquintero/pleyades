from jsonschema import Draft4Validator, draft4_format_checker

login_schema = {
    "type": "object",
    "properties": {
        "email":  {"type": "string", "format": "email", "maxLength": 200},
        "password":  {"type": "string", "maxLength": 50},
    },
    "required": ["email", "password"],
    "additionalProperties": False
}


def validate_login_schema(json):
    return Draft4Validator(login_schema, format_checker=draft4_format_checker).is_valid(json)
