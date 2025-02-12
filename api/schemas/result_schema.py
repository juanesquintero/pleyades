from jsonschema import Draft4Validator

post_schema = {
    "type": "array",
    "items": {
            "type": "object",
            "properties": {
                "documento":  {"type": "string", "maxLength": 100},
                "name_completo":  {"type": "string", "maxLength": 300},
                "idprograma":  {"type": "integer", "maxLength": 30},
                "prediccion":  {"type": "integer", "maxLength": 1},
                "desertor":  {"type": "integer", "maxLength": 1},
                "semestre_prediccion": {"type": "integer", "maxLength": 30},
            },
        "required": ["documento", "name_completo", "idprograma", "prediccion", "semestre_prediccion", "desertor"],
        "additionalProperties": True
    }

}


def validate_post_schema(json):
    return Draft4Validator(post_schema, format_checker=Draft4Validator.FORMAT_CHECKER).is_valid(json)
