"""
An EventBus intended to handle registration and deregistration of events
using the ib_async API.
"""

class EventBus:

    def __init__(self):
        self._registry = dict()
        self.custom_events = dict()

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
            key = f"{getattr(func, '__module__', '')}.{getattr(func, '__qualname__', repr(func))}"
            assert self._registry[key] is not None
            if set(self._registry[func]).intersection(set(args)):
                self._registry[func] = list(
                    set(self._registry[func]) - (set(args))
                )

    def listen(self, func, *args) -> None:
        key = f"{getattr(func, '__module__', '')}. {getattr(func, '__qualname__', repr(func))}"
        try:
            self._registry[key]
        except KeyError:
            self._registry[key] = []
        for event in args:
            if event not in self._registry[key]:
                event += func
                self._registry[key].append(event)

    def stop_listening(self, func, *args) -> None:
        key = f"{getattr(func, '__module__', '')}.{getattr(func, '__qualname__', repr(func))}"
        for event in args:
            if event in self._registry[key]:
                event -= func
                self._registry[key].remove(event)

    def stop_listening_all(self, func) -> None:
        key = f"{getattr(func, '__module__', '')}.{getattr(func, '__qualname__', repr(func))}"
        for event in self.get_events():
            if event in self._registry[key]:
                event -= func
        self._registry.pop(key)

    def add_custom_event(self, name, event):
        self.custom_events[name] = event

    def remove_custom_event(self, name):
        self.custom_events.pop(name)

    def fire_custom_event(self, name, *args):
        self.custom_events[name](*args)

BusSingleton = EventBus()
