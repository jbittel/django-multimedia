def get_callable(path):
    """Return a callable from a given dotted path."""
    try:
        module_path, callable_name = path.rsplit('.', 1)
    except ValueError:
        raise ImportError("%s doesn't look like a callable path" % path)

    module = __import__(module_path, fromlist=[''])

    try:
        return getattr(module, callable_name)
    except AttributeError:
        raise ImportError("Could not import %s from module %s" %
                          (callable_name, module_path))
