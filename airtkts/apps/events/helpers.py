from guardian.shortcuts import get_objects_for_user


def get_events(entity):

    return get_objects_for_user(entity, 'events.view_event')