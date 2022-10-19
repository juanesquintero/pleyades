from jsonschema import Draft4Validator, draft4_format_checker

post_schema = {
    "type": "object",
    "properties": {
        "facultad":  {"type": "integer", "maxLength": 30},
        "codigo":  {"type": "integer", "maxLength": 30},
        "nombre_corto":  {"type": "string", "maxLength": 10},
        "nombre":  {"type": "string", "maxLength": 200},
        "nombre_facultad":  {"type": "string", "maxLength": 200, "minLength": 1},
    },
    "required": [ "facultad", "codigo", "nombre_corto", "nombre", "nombre_facultad"],
    "additionalProperties": False
}

put_schema = {
   "type": "object",
   "minProperties": 1,
    "properties": {
        "nombre_corto":  {"type": "string", "maxLength": 10},
        "nombre":  {"type": "string", "maxLength": 200},
    },
    "additionalProperties": False
}

def validate_post_schema(json):
    return Draft4Validator(post_schema,format_checker=draft4_format_checker).is_valid(json)

def validate_put_schema(json):
    return Draft4Validator(put_schema,format_checker=draft4_format_checker).is_valid(json)