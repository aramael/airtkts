"""
Django views for airtkts project.

"""

from django.shortcuts import render, redirect, get_object_or_404
from airtkts.apps.events.forms import EventForm, TicketSaleForm, TicketOfficeSaleForm, InviteForm, QuickInviteForm
from airtkts.apps.events.models import Event, TicketSale, Invitation
from .helpers import has_model_permissions, has_global_permissions
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from airtkts.libs.users.managers import UserManager
from airtkts.libs.users.forms import UserCreationForm, UserEditForm


def home(request):
    """    Display the Landing Page    """

    context = {}

    return render(request, '', context)


def ticket_office(request, event_id=None, event_slug=None):

    if event_id is not None:
        event = get_object_or_404(Event, pk=event_id)
        if event_slug != event.slug:
            redirect('ticket_office', event_id=event.pk, event_slug=event.slug)
    else:
        event = None

    form = TicketOfficeSaleForm(data=request.POST or None, files=request.FILES or None)

    context = {
        'event': event,
        'form': form,
    }

    return render(request, 'ticket_office_home.html', context)


def event_home(request):
    """    Display the Landing Page    """

    events = Event.objects.all()

    context = {
        'events': events,
    }

    return render(request, 'event_home.html', context)

def event_dashboard(request, event_id=None):

    event = get_object_or_404(Event, pk=event_id)

    context = {
        'event': event,
    }

    return render(request, 'event_dashboard.html', context)


def event_form(request, event_id=None, event_slug=None):
    """    Display the Landing Page    """

    if event_id is not None:
        event = get_object_or_404(Event, pk=event_id)
    else:
        event = None

    form = EventForm(instance=event, initial={'owners': [request.user, ], }, data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save()
        return redirect(**location_redirect)

    context = {
        'form': form,
        'event': event,
    }

    return render(request, 'event_form.html', context)


def invites_home(request, event_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    invites = Invitation.objects.filter(event=event)

    context = {
        'invites': invites,
        'event': event,
    }

    return render(request, 'invite_home.html', context)


def invites_form(request, event_id=None, invite_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    if invite_id is not None:
            invite = get_object_or_404(Invitation, pk=invite_id)
    else:
        invite = None

    initial_data = {'event': event, }

    if 'quick' in request.GET:
        form_class = QuickInviteForm
        template = 'invite_quick_form.html'
    else:
        form_class = InviteForm
        template = 'invite_form.html'

    form = form_class(instance=invite, initial=initial_data,
                      data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save()
        return redirect(**location_redirect)

    context = {
        'form': form,
        'invite': invite,
        'event': event,
    }

    return render(request, template, context)


def ticketsales_home(request, event_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    sales = TicketSale.objects.filter(event=event)

    context = {
        'sales': sales,
        'event': event,
    }

    return render(request, 'ticketsales_home.html', context)


def ticketsales_form(request, event_id=None, ticket_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    if ticket_id is not None:
            ticket = get_object_or_404(TicketSale, pk=ticket_id)
    else:
        ticket = None

    form = TicketSaleForm(instance=ticket, initial={'event':event, }, data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save()
        return redirect(**location_redirect)

    context = {
        'form': form,
        'ticket': ticket,
        'event': event,
    }

    return render(request, 'ticketsales_form.html', context)

#==============================================================================
# Users Pages
#==============================================================================

@login_required
def users_home(request):

    if not has_global_permissions(request.user, UserManager, 'change', 'auth'):
        return HttpResponseForbidden('403 Forbidden')

    manager = UserManager()

    if request.POST:
        if '_bulkactions' in request.POST:

            items = []
            for item in request.POST.getlist('_selected_action'):
                item = User.objects.get(pk=int(item))
                items.append(item)

            manager.process_bulk_actions(request=request, action=request.POST['action'], queryset=items)

    users = User.objects.all()

    context = {
        'users': users,
        "actions": manager.bulk_actions ,
    }

    return render(request, 'users_home.html', context)

@login_required
def users_new(request):

    if not has_global_permissions(request.user, UserManager, 'add', 'auth'):
        return HttpResponseForbidden('403 Forbidden')

    form = UserCreationForm(data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save()
        return redirect(**location_redirect)

    context = {
        'form': form,
    }

    return render(request, 'users_new.html', context)

@login_required
def users_edit(request, user_id=None, self_edit=False):

    if not has_global_permissions(request.user, UserManager, 'change', 'auth'):
        return HttpResponseForbidden('403 Forbidden')

    if self_edit:
        user = request.user
    else:
        user = get_object_or_404(User, pk=user_id)

    form = UserEditForm(instance=user, data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save()
        return redirect(**location_redirect)

    context = {
        'form': form
    }

    return render(request, 'users_edit.html', context)