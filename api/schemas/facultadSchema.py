from jsonschema import Draft4Validator, draft4_format_checker

post_schema = {
    "type": "object",
    "properties": {
        "codigo":  {"type": "integer", "maxLength": 30},
        "nombre":  {"type": "string", "maxLength": 200},
    },
    "required": [ "nombre", "codigo" ],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "nombre":  {"type": "string", "maxLength": 200},
    },
    "additionalProperties": False
}

def validate_post_schema(json):
    return Draft4Validator(post_schema,format_checker=draft4_format_checker).is_valid(json)

def validate_put_schema(json):
    return Draft4Validator(put_schema,format_checker=draft4_format_checker).is_valid(json)
    
