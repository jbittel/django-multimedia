from django.core.exceptions import ImproperlyConfigured

try:
    from importlib import import_module
except ImportError:
    from django.utils.importlib import import_module


def import_by_path(dotted_path):
    """
    Import a dotted module path and return the attribute/class
    designated by the last name in the path. Raise ImproperlyConfigured
    if something goes wrong.

    Reproduced and slightly modified from the Django 1.6 source for
    compatibility with older Django versions.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        raise ImproperlyConfigured(msg)
    try:
        module = import_module(module_path)
    except ImportError as e:
        msg = "Error importing module %s: %s" % (module_path, e)
        raise ImproperlyConfigured(msg)
    try:
        attr = getattr(module, class_name)
    except AttributeError:
        msg = "Module %s does not define a '%s' attribute/class" % (
            module_path, class_name)
        raise ImproperlyConfigured(msg)
    return attr
