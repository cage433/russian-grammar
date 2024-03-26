__all__ = [
    "checked_subclass",
    "checked_type",
    "checked_list_type",
    "checked_optional_type",
    "checked_dict_type",
    "tuple_type_checker",
]


def checked_subclass(obj_type, parent_type):
    assert issubclass(obj_type, parent_type), f"{obj_type} is not a subclass of {parent_type}"
    return obj_type


def checked_type(obj, expected_type):
    if isinstance(expected_type, (type, list, tuple)):
        assert isinstance(obj, expected_type), f"{obj} is of type {type(obj)}, expected {expected_type}"
        return obj

    if callable(expected_type):
        expected_type(obj)
        return obj
    raise ValueError(f"Expected either a type or a callable, got {expected_type}")


def checked_list_type(obj, expected_type):
    assert isinstance(obj, list), f"{obj} is of type {type(obj)}, expected list"
    for x in obj:
        checked_type(x, expected_type)
    return obj


def checked_optional_type(obj, expected_type):
    if obj is None:
        return None
    return checked_type(obj, expected_type)


def checked_dict_type(obj, key_type, value_type):
    assert isinstance(obj, dict), f"{obj} is of type {type(obj)}, expected list"
    for k, v in obj.items():
        checked_type(k, key_type)
        checked_type(v, value_type)
    return obj


def tuple_type_checker(*types):
    def check(obj):
        assert len(obj) == len(types), f"Expected tuple size to be ${len(types)}, got {obj}"
        for o, t in zip(obj, types):
            checked_type(o, t)

    return check
