from guardian.shortcuts import get_objects_for_user
from django.contrib.auth.models import User
from .models import TicketSale


def get_events(entity):

    return get_objects_for_user(entity, 'events.view_event')


def get_available_sales(entity):

    if entity is not None:

        queryset = entity.available_sales.all()

        if type(entity.user) is User:
            if entity.user.has_perm('events.view_event_ticketsale', entity.event):
                queryset = TicketSale.objects.filter(event=entity.event)

    else:
        queryset = TicketSale.objects.get_empty_query_set()

    return queryset