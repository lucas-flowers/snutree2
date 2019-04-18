

def get(mapping, *args):
    value = mapping
    for arg in args:
        value = value.get(arg, {})
    return value

