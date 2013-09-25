"""
Django views for airtkts project.

"""

from django.shortcuts import render, redirect, get_object_or_404
from airtkts.apps.events.forms import EventForm
from airtkts.apps.events.models import Event


def home(request):
    """    Display the Landing Page    """

    context = {}

    return render(request, '', context)


def event_home(request):
    """    Display the Landing Page    """

    events = Event.objects.all()

    context = {
        'events': events,
    }

    return render(request, 'event_home.html', context)


def event_form(request, event_id=None, event_slug=None):
    """    Display the Landing Page    """

    if event_id is not None:
        event = get_object_or_404(Event, pk=event_id)
        if event_slug != event.slug:
            redirect('event_edit', event_id=event.pk, event_slug=event.slug)
    else:
        event = None

    form = EventForm(instance=event, data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save()
        return redirect(**location_redirect)

    context = {
        'form': form,
        'event': event,
    }

    return render(request, 'event_form.html', context)