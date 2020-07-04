def system_import(sys, **config):
    module_name = 'drop_box' if sys == 'dropbox' else sys.lower()
    try:
        from importlib import import_module
        class_ = getattr(import_module("systems.%s" % module_name), sys.capitalize())
        system_instance = class_(**config)
    except ImportError as e:
        print(e)

    return system_instance
