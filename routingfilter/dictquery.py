class DictQuery(dict):
    """https://www.haykranen.nl/2016/02/13/handling-complex-nested-dicts-in-python/"""

    def get(self, path, default=None):
        # In some very weird cases we can have a dict key written like "foo.bar"
        # If it exists we do not traverse the dictionary
        value = dict.get(self, path)
        if value:
            return value
        keys = path.split('.')
        value = None
        try:
            for key in keys:
                if value:
                    if isinstance(value, list):
                        value = [v.get(key, default) if v else None for v in value]
                    else:
                        value = value.get(key, default)
                else:
                    value = dict.get(self, key, default)

                if not value:
                    break
        except AttributeError:
            # If dict is like this { "foobar": 1} and path is foobar.test it would generate
            # an AttributeError. We manage this case like a failed match
            value = default
        return value
