from jsonschema import Draft4Validator

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
    return Draft4Validator(
        login_schema,
        format_checker=Draft4Validator.FORMAT_CHECKER
    ).is_valid(json)
