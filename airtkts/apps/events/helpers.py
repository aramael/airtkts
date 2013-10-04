from .models import Event


def get_events(entity):

    kwargs = {
        'owner': entity,
    }

    # Active superusers have all permissions.
    if entity.is_active and entity.is_superuser:
        kwargs = {}

    return Event.objects.filter(**kwargs)