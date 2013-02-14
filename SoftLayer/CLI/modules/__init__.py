from pkgutil import iter_modules


def get_module_list():
    actions = [action[1] for action in iter_modules(__path__)]
    return actions
