from jsonschema import Draft4Validator, draft4_format_checker

nombre_schema = {
    "type": "object",
    "properties": {
        "programa":  {"type": "integer", "maxLength": 30},
        "encargado":   {"type": "string", "format": "email", "maxLength": 200},
        "tipo":  {"type": "string", "maxLength": 50},
        "periodoInicial":  {"type": "integer", "maxLength": 6},
        "periodoFinal":  {"type": "integer", "maxLength": 6},
        "estado":  {"type": "string", "maxLength": 50},
    },
    "required": ["programa","encargado","tipo","periodoInicial","periodoFinal","estado"],
    "additionalProperties": False
}

post_schema = {
    "type": "object",
    "properties": {
        "nombre": {"type": "string", "maxLength": 200},
        "numero": {"type": "integer", "maxLength": 30},
        "programa":  {"type": "integer", "maxLength": 30},
        "encargado":   {"type": "string", "format": "email", "maxLength": 200},
        "tipo":  {"type": "string", "maxLength": 50},
        "periodoInicial":  {"type": "integer", "maxLength": 6},
        "periodoFinal":  {"type": "integer", "maxLength": 6},
        "estado":  {"type": "string", "maxLength": 50},
    },
    "required": ["nombre","programa","encargado","tipo","periodoInicial","periodoFinal","estado"],
    "additionalProperties": False
}

put_schema = {
    "type": "object",
    "minProperties": 1,
    "properties": {
        "encargado":   {"type": "string", "format": "email", "maxLength": 200},
        "estado":  {"type": "string", "maxLength": 50},
    },
    "additionalProperties": False
}

def validate_nombre_schema(json):
    return Draft4Validator(nombre_schema, format_checker=draft4_format_checker).is_valid(json)

def validate_post_schema(json):
    return Draft4Validator(post_schema, format_checker=draft4_format_checker).is_valid(json)

def validate_put_schema(json):
    return Draft4Validator(put_schema, format_checker=draft4_format_checker).is_valid(json)
