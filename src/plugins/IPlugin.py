# Copyright 2009, Alvaro J. Iradier
# This file is part of xPressent.
#
# xPressent is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# xPressent is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with xPressent.  If not, see <http://www.gnu.org/licenses/>.

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
