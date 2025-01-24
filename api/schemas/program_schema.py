from jsonschema import Draft4Validator, draft4_format_checker

post_schema = {
    "type": "object",
    "properties": {
        "faculty":  {"type": "integer", "maxLength": 30},
        "codigo":  {"type": "integer", "maxLength": 30},
        "name_corto":  {"type": "string", "maxLength": 10},
        "name":  {"type": "string", "maxLength": 200},
        "name_faculty":  {"type": "string", "maxLength": 200, "minLength": 1},
    },
    "required": ["faculty", "codigo", "name_corto", "name", "name_faculty"],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "name_corto":  {"type": "string", "maxLength": 10},
        "name":  {"type": "string", "maxLength": 200},
    },
    "additionalProperties": False
}


def validate_post_schema(json):
    return Draft4Validator(post_schema, format_checker=draft4_format_checker).is_valid(json)


def validate_put_schema(json):
    return Draft4Validator(put_schema, format_checker=draft4_format_checker).is_valid(json)
