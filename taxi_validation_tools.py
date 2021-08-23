from functools import wraps
from typing import Callable, Any, Dict

import jsonschema
from flask import request, Response

post_drivers_schema = {
    "type": "object",
    "examples": [{"name": "Bob"}, {"car": "Audi A6"}],
    "required": ["name", "car"],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "car": {"type": "string", "minLength": 1},
    },
}


post_clients_schema = {
    "type": "object",
    "examples": [{"name": "Bill"}, {"is_vip": "true"}],
    "required": ["name", "is_vip"],
    "additionalProperties": False,
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "is_vip": {"type": "boolean"},
    },
}


post_orders_schema = {
    "type": "object",
    "examples": [
        {"client_id": 1},
        {"driver_id": 3},
        {"date_created": "2021-08-21T19:36:08.206Z"},
        {"status": "not_accepted"},
        {"address_from": "Moscow"},
        {"address_to": "Saint-Petersburg"},
    ],
    "required": ["client_id", "driver_id", "status", "address_from", "address_to"],
    "additionalProperties": False,
    "properties": {
        "client_id": {"type": "integer"},
        "driver_id": {"type": "integer"},
        "date_created": {"type": "string", "format": "date-time"},
        "status": {
            "type": "string",
            "enum": ["not_accepted", "in_progress", "done", "cancelled"],
        },
        "address_from": {"type": "string", "minLength": 1},
        "address_to": {"type": "string", "minLength": 1},
    },
}


put_orders_schema = {
    "type": "object",
    "examples": [
        {"client_id": 1},
        {"driver_id": 3},
        {"date_created": "2021-08-21T19:36:08.206Z"},
        {"status": "not_accepted"},
        {"address_from": "Moscow"},
        {"address_to": "Saint-Petersburg"},
    ],
    "additionalProperties": False,
    "properties": {
        "client_id": {"type": "integer"},
        "driver_id": {"type": "integer"},
        "date_created": {"type": "string", "format": "date-time"},
        "status": {
            "type": "string",
            "enum": ["not_accepted", "in_progress", "done", "cancelled"],
        },
        "address_from": {"type": "string", "minLength": 1},
        "address_to": {"type": "string", "minLength": 1},
    },
}


def validate_json(schema_name: Dict[str, object]) -> Callable:
    """Декоратор для валидации json-данных, отправляемых сервису заказа такси в HTTP-запросе."""

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                jsonschema.validate(request.json, schema_name)
            except jsonschema.ValidationError:
                return Response("Bad Request", status=400)
            return function(*args, **kwargs)

        return wrapper

    return decorator


def validate_url_variable(variable: str) -> Callable:
    """Декоратор для валидации переменных, переданных сервису заказа такси через HTTP-запрос."""

    def decorator(function: Callable) -> Callable:
        @wraps(function)
        def wrapper(**kwargs: Any) -> Any:
            url_argument = request.args.get(variable)
            if url_argument is not None:
                if url_argument.isdigit():
                    return function(**kwargs)
                else:
                    return Response("Bad Request", status=400)
            elif isinstance(kwargs[variable], int):
                return function(**kwargs)
            else:
                return Response("Bad Request", status=400)

        return wrapper

    return decorator
