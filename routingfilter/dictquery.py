class DictQuery(dict):
    # https://www.haykranen.nl/2016/02/13/handling-complex-nested-dicts-in-python/

    def get(self, path, default=None):
        """Reimplement get method to walk the path on a dictionary.

        Keep in mind if the dictionary contains a key with a ``.`` inside it will be matched first. Example:

        ::

            mydict = {
                "foo.bar": 42,
                "foo": {
                    "bar": 1,
                    "baz": "hello"
                }
            }

            mydictquery = DictQuery(mydict)
            mydictquery.get("foo.bar") # returns 42
            mydictquery.get("foo.baz") # returns hello


        :param path: path to match
        :type path: string
        :param default: default return value, defaults to None
        :type default: obj, optional
        :return: matched values or None
        :rtype: obj
        """
        value = dict.get(self, path)
        if value:
            return value

        keys = path.split(".")
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
            # This happens when dictionary contains a field the partially overlaps with path
            # ES: mydict = { "source": "foobar"} path = "source.ip"
            # The for above searches for "source" and value became "foobar", then it tries to do "foobar".get("ip")
            # but foobar is not a dictionary and it fails.
            # We set value to None because the searched path ("source.ip") is not present on mydict
            value = default

        return value

    def set(self, path, value):
        keys = path.split(".")

        key = keys.pop()
        tmp = {key: value}
        while keys:
            key = keys.pop()
            tmp = {key: tmp}
        self.update(tmp)


class CachedDictQuery(DictQuery):
    """Event wrapper memoising get() for the lifetime of one Routing.match() call: set() and update() do not invalidate the cache."""

    # Rule.match updates this path in place during a match() call, so its lookups must never be cached
    UNCACHED_PATH_PREFIX = "certego.routing_history"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lookup_cache = {}

    def get(self, path, default=None):
        """Same as DictQuery.get, cached by (path, repr(default)) since the default can end up inside list results."""
        key = (path, repr(default))
        try:
            return self._lookup_cache[key]
        except KeyError:
            pass
        value = super().get(path, default)
        # Checked only on a miss: uncacheable paths are never stored, so a hit can never serve one
        if isinstance(path, str) and not path.startswith(self.UNCACHED_PATH_PREFIX):
            self._lookup_cache[key] = value
        return value
