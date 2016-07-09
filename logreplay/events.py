__all__ = ["response", "repeat", "replay"]


class EventHook:

    def __init__(self):
        self._handlers = []

    def __iadd__(self, other):
        self._handlers.append(other)
        return self

    def __isub__(self, other):
        self._handlers.remove(other)
        return self

    def fire(self, **kwargs):
        for handler in self._handlers:
            handler(**kwargs)


repeat = EventHook()  # arguments: parameters
replay = EventHook()
