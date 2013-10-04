"""
Django views for airtkts project.

"""

import json

from .helpers import has_model_permissions, has_global_permissions
from airtkts.apps.events.forms import EventForm, TicketSaleForm, TicketOfficeSaleForm, InviteForm, QuickInviteForm
from airtkts.apps.events.helpers import get_events
from airtkts.apps.events.models import Event, TicketSale, Invitation
from airtkts.libs.users.forms import UserCreationForm, UserEditForm
from airtkts.libs.users.managers import UserManager
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404


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

    context = {
        'events': get_events(request.user),
    }

    return render(request, 'event_home.html', context)


def event_dashboard(request, event_id=None):

    event = get_object_or_404(Event, pk=event_id)

    context = {
        'event': event,
        'events': get_events(request.user),
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
        'events': get_events(request.user),
    }

    return render(request, 'event_form.html', context)


def invites_home(request, event_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    invites = Invitation.objects.filter(event=event)

    context = {
        'invites': invites,
        'event': event,
        'events': get_events(request.user),
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
        'events': get_events(request.user),
    }

    return render(request, template, context)


def ticketsales_home(request, event_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    sales = TicketSale.objects.filter(event=event)

    context = {
        'sales': sales,
        'event': event,
        'events': get_events(request.user),
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
        'events': get_events(request.user),
    }

    return render(request, 'ticketsales_form.html', context)

#==============================================================================
# Account Pages
#==============================================================================

@login_required
def accounts_home(request):

    context = {
        'events': get_events(request.user),
    }

    return render(request, 'accounts/accounts_home.html', context)

@login_required
def host_search(request):
    if 'q' in request.GET:
        query = request.GET['q']

        hosts = User.objects.filter(Q(username__iexact=query) | Q(first_name__iexact=query) | Q(last_name__iexact=query) | Q(email__iexact=query))

        results = []

        for host in hosts:
            results.append({
                'value': host.pk,
                'tokens': [
                    host.username,
                    host.first_name,
                    host.last_name
                ],
                'name': host.get_full_name() if host.get_full_name() != '' else host.username
            })

        return HttpResponse(json.dumps(results))

    return HttpResponseForbidden('403 Forbidden')


@login_required
def hosts_home(request, event_id=None):

    event = get_object_or_404(Event, pk=event_id)

    #if not has_model_permissions(request.user, 'change', event) or not has_global_permissions(request.user, Event, 'change', 'events'):
    #    return HttpResponseForbidden('403 Forbidden')

    if request.is_ajax() and 'action' in request.POST:
        errors = []
        computer_errors = []
        if request.POST['action'] == 'remove_host' and 'host' in request.POST:

            try:
                host = User.objects.get(pk=request.POST['host'])
            except User.DoesNotExist:
                computer_errors.append('User does not exist')
            else:
                if host != request.user:
                    event.owner.remove(host)
                    return HttpResponse(json.dumps({'success': True, }))
                else:
                    errors.append('You can not remove your self from your own event')
        else:
            computer_errors.append('Invalid Action or not all required params are given.')

        return HttpResponse(json.dumps({'success': False, 'errors': errors, '_e': computer_errors}))




    context = {
        'event': event,
        'events': get_events(request.user),
    }
    return render(request, 'events/hosts_home.html', context)


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
        'events': get_events(request.user),
        "actions": manager.bulk_actions,
    }

    return render(request, 'accounts/users_home.html', context)

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
        'events': get_events(request.user),
    }

    return render(request, 'accounts/users_new.html', context)

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
        'form': form,
        'events': get_events(request.user),
    }

    return render(request, 'accounts/users_edit.html', context)