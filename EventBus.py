"""
An EventBus intended to handle registration and deregistration of events
using the ib_async API.
"""

class EventBus:

    def __init__(self):
        self._registry = dict()

    def get_registry(self) -> dict:
        return self._registry

    def get_registered_functions(self) -> list:
        return list(self._registry.keys())

    def __get_events__(self):
        for events in list(self._registry.values()):
            for event in events:
                yield event

    def get_events(self) -> list:
        return list(set(self.__get_events__()))

    def remove_events(self, *args) -> None:
        for func in list(self._registry.keys()):
            key = f"{func.__module__}.{func.__qualname__}"
            assert self._registry[key] is not None
            if set(self._registry[func]).intersection(set(args)):
                self._registry[func] = list(
                    set(self._registry[func]) - (set(args))
                )

    def listen(self, func, *args) -> None:
        key = f"{func.__module__}.{func.__qualname__}"
        try:
            self._registry[key]
        except KeyError:
            self._registry[key] = []
        for event in args:
            if event not in self._registry[key]:
                event += func
                self._registry[key].append(event)

    def stop_listening(self, func, *args) -> None:
        key = f"{func.__module__}.{func.__qualname__}"
        for event in args:
            if event in self._registry[key]:
                event -= func
                self._registry[key].remove(event)

    def stop_listening_all(self, func) -> None:
        key = f"{func.__module__}.{func.__qualname__}"
        for event in self.get_events():
            if event in self._registry[key]:
                event -= func
        self._registry.pop(key)
