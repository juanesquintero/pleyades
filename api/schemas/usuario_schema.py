from jsonschema import Draft4Validator, draft4_format_checker

post_schema = {
    "type": "object",
    "properties": {
        "nombre":  {"type": "string", "maxLength": 200},
        "correo":  {"type": "string", "format": "email","maxLength": 200},  
        "clave":  {"type": "string", "maxLength": 50, "minLength":8 },
        "rol":  {"type": "string", "maxLength": 50},
    },
    "required": ["nombre", "correo", "clave", "rol"],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "nombre":  {"type": "string", "maxLength": 200},
        "clave":  {"type": "string", "maxLength": 50, "minLength":8 },
        "rol":  {"type": "string", "maxLength": 50},
    },
    "additionalProperties": False
}

def validate_post_schema(json):
    return Draft4Validator(post_schema,format_checker=draft4_format_checker).is_valid(json)

def validate_put_schema(json):
    return Draft4Validator(put_schema,format_checker=draft4_format_checker).is_valid(json)
