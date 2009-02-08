
EVENT_SLIDECHANGE = 1000

event_listeners = {}

def register_event_listener(event_type, listener_function):
    if event_listeners.has_key(event_type):
        event_listeners[event_type].append(listener_function)
    else:
        event_listeners[event_type] = [listener_function]

def fire_event(event_type, event_args):
    if not event_listeners.has_key(event_type): return
    for listener in event_listeners[event_type]:
        listener(*event_args)

class IPlugin():
    pass
