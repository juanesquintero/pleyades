from jsonschema import Draft4Validator, draft4_format_checker

post_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string", "maxLength": 250},
        "set":  {"type": "string", "maxLength": 200},
        "numero": {"type": "integer", "maxLength": 30},
        "preparador":   {"type": "string", "format": "email", "maxLength": 200},
        "fechaInicial":  {"type": "string", "format": "date-time"},
        "fechaFinal":  {"type": ["string", "null"], "format": "date-time"},
        "estado":  {"type": "string", "maxLength": 50, "enum": ["Fallida", "Exitosa"]},
        "observaciones":  {"type": ["object", "null"]},
    },
    "required": ["nombre", "numero", "set", "preparador", "fechaInicial", "fechaFinal", "estado"],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "estado":  {"type": "string", "maxLength": 50, "enum": ["Fallida", "Exitosa"]},
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
