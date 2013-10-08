"""
Django views for airtkts project.

"""

import json

from airtkts.apps.events.forms import EventForm, HostForm, InviteForm, QuickInviteForm, \
    TicketOfficeSaleForm, TicketSaleForm, LimitedInviteForm, GuestInviteForm
from airtkts.apps.events.helpers import get_events
from airtkts.apps.events.models import Event, Invitation, TicketSale
from airtkts.libs.users.forms import UserCreationForm, UserEditForm
from airtkts.libs.users.managers import UserManager, send_new_event_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from guardian.shortcuts import assign_perm, get_perms, remove_perm


def home(request):
    """    Display the Landing Page    """

    context = {}

    return render(request, '', context)


def invite_serve(request, invite_key=None):

    location_redirect = Invitation.objects.serve_invite(invite_key=invite_key)

    if location_redirect.get('invite', False):
        request.session['invite_id'] = location_redirect.get('invite')

        del location_redirect['invite']

    return redirect(**location_redirect)


def invite_invalid(request):
    return render(request, 'ticket_office/invite_invalid.html')


def invite_expired(request, event_id=None):

    try:
        event = Event.objects.get(pk=event_id)
    except Event.DoesNotExist:
        return redirect('invite_invalid')

    return render(request, 'ticket_office/invite_expired.html', {'event': event})


def ticket_office(request, event_id=None, event_slug=None):
    if event_id is not None:
        event = get_object_or_404(Event, pk=event_id)
        if event_slug != event.slug:
            redirect('ticket_office', event_id=event.pk, event_slug=event.slug)
    else:
        event = None

    initial = {}

    if request.session.get('invite', False):

        invite = get_object_or_404(Invitation, pk=request.session.get('invite'))

        initial['first_name'] = invite.first_name
        initial['last_name'] = invite.last_name
        initial['email'] = invite.email

    form = TicketOfficeSaleForm(initial=initial, data=request.POST or None, files=request.FILES or None)

    context = {
        'event': event,
        'form': form,
    }

    return render(request, 'ticket_office_home.html', context)


#==============================================================================
# Event Pages
#==============================================================================


@login_required
def event_home(request):
    """    Display the Landing Page    """

    if request.POST:
        if '_bulkactions' in request.POST:

            items = []
            for item in request.POST.getlist('_selected_action'):
                item = Event.objects.get(pk=int(item))
                items.append(item)

            Event.objects.process_bulk_actions(request=request, action=request.POST['action'], queryset=items)

    context = {
        'actions': Event.objects.bulk_actions,
        'events': get_events(request.user),
    }

    return render(request, 'events/event_home.html', context)

# =======================================
# Event Edit Pages
# =======================================


@login_required
def event_dashboard(request, event_id=None):
    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm('events.view_event', event):
        return HttpResponseForbidden('403 Forbidden')

    context = {
        'event': event,
        'events': get_events(request.user),
    }

    return render(request, 'events/event_dashboard.html', context)


@login_required
def event_form(request, event_id=None, event_slug=None):
    """    Display the Landing Page    """

    if event_id is not None:
        event = get_object_or_404(Event, pk=event_id)
        if not request.user.has_perm('events.change_event', event):
            return HttpResponseForbidden('403 Forbidden')
    else:
        event = None
        if not request.user.has_perm('events.add_event'):
            return HttpResponseForbidden('403 Forbidden')

    form = EventForm(instance=event, initial={'owner': [request.user, ], }, data=request.POST or None,
                     files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save(request=request)
        return redirect(**location_redirect)

    context = {
        'section': 'event',
        'extends': 'events/event_new.html' if event is None else 'events/system_base.html',
        'form': form,
        'event': event,
        'events': get_events(request.user),
    }

    return render(request, 'events/event_form.html', context)


# =======================================
# Ticket Sales Pages
# =======================================


@login_required
def ticketsales_home(request, event_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm('events.add_event_ticketsale', event):
        return HttpResponseForbidden('403 Forbidden')

    sales = TicketSale.objects.filter(event=event)

    if request.POST:
        if '_bulkactions' in request.POST:

            items = []
            for item in request.POST.getlist('_selected_action'):
                item = TicketSale.objects.get(pk=int(item))
                items.append(item)

            TicketSale.objects.process_bulk_actions(request=request, action=request.POST['action'], queryset=items)

    context = {
        'section': 'ticketsales',
        'actions': TicketSale.objects.bulk_actions,
        'sales': sales,
        'event': event,
        'events': get_events(request.user),
    }

    return render(request, 'events/ticketsales_home.html', context)


@login_required
def ticketsales_form(request, event_id=None, ticket_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm('events.add_event_ticketsale', event):
        return HttpResponseForbidden('403 Forbidden')

    if ticket_id is not None:
        ticket = get_object_or_404(TicketSale, pk=ticket_id)
    else:
        ticket = None

    form = TicketSaleForm(instance=ticket, initial={'event': event, }, data=request.POST or None,
                          files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save()
        return redirect(**location_redirect)

    context = {
        'section': 'ticketsales',
        'form': form,
        'ticket': ticket,
        'event': event,
        'events': get_events(request.user),
    }

    return render(request, 'events/ticketsales_form.html', context)


# =======================================
# Invites Pages
# =======================================


@login_required
def invites_home(request, event_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm('events.view_event', event):
        return HttpResponseForbidden('403 Forbidden')

    if request.POST:
        if '_bulkactions' in request.POST:

            items = []
            for item in request.POST.getlist('_selected_action'):
                item = Invitation.objects.get(pk=int(item))
                items.append(item)

            Invitation.objects.process_bulk_actions(request=request, action=request.POST['action'], queryset=items)

    invites = Invitation.objects.filter(event=event)

    context = {
        'section': 'invites',
        'actions': Invitation.objects.bulk_actions,
        'invites': invites,
        'event': event,
        'events': get_events(request.user),
    }

    return render(request, 'events/invite_home.html', context)


@login_required
def invites_form(request, event_id=None, invite_id=None):
    """    Display the Landing Page    """

    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm('events.view_event', event):
        return HttpResponseForbidden('403 Forbidden')

    if invite_id is not None:
        invite = get_object_or_404(Invitation, pk=invite_id)
    else:
        invite = None

    user_invite = Invitation.objects.get(user=request.user, event=event)

    if invite is not None and not request.user.has_perm('events.view_invitation', invite):
        return HttpResponseForbidden('403 Forbidden')

    form_class = InviteForm
    template = 'events/invite_form.html'

    if invite is None and 'quick' in request.GET:
        # Pass Along the QuickInvite Form for new guests
        form_class = QuickInviteForm
        template = 'events/invite_quick_form.html'
    elif invite is not None:

        if invite.invited_by is not None and invite.invited_by.pk == user_invite.pk:
            # The guest is only allowed to edit some things on their own guests
            # Show the invite form for own guests
            form_class = GuestInviteForm
            template = 'events/invite_guest_form.html'

        if not request.user.has_perm('events.change_hosts', event):
            # If the user is trying to see their own invite
            # they can once again only see certain events.
            form_class = LimitedInviteForm
            template = 'events/invite_limited_form.html'

    if request.user.has_perm('events.change_hosts', event):
        # If the user can change the hosts then give all public data
        form_class = InviteForm
        template = 'events/invite_form.html'

    form = form_class(event=event, user=request.user, instance=invite, initial={'event': event, 'invited_by': user_invite, },
                      data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save(request)
        return redirect(**location_redirect)

    context = {
        'section': 'invites',
        'form': form,
        'invite': invite,
        'event': event,
        'events': get_events(request.user),
    }

    return render(request, template, context)

# =======================================
# Host Pages
# =======================================


@login_required
def host_search(request):
    if not request.user.has_perm('events.search_hosts'):
        return HttpResponseForbidden('403 Forbidden')

    if 'q' in request.GET:
        query = request.GET['q']

        hosts = User.objects.filter(
            Q(username__icontains=query) | Q(first_name__icontains=query) | Q(last_name__icontains=query) | Q(
                email__icontains=query))

        results = []

        for host in hosts:
            name = host.get_full_name() if host.get_full_name() != '' else host.username

            tokens = filter(None, [
                host.username,
                host.first_name,
                host.last_name,
                name
            ])

            results.append({
                'value': host.username,
                'tokens': tokens,
                'name': name,
                'pk': host.pk
            })

        return HttpResponse(json.dumps(results))

    return HttpResponseForbidden('403 Forbidden')


@login_required
def hosts_new(request, event_id=None):
    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm('events.add_hosts', event):
        return HttpResponseForbidden('403 Forbidden')

    form = HostForm(data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        location_redirect = form.save(request, event)
        return redirect(**location_redirect)

    context = {
        'section': 'hosts',
        'form': form,
        'event': event,
        'events': get_events(request.user),
    }
    return render(request, 'events/hosts_new.html', context)


@login_required
def hosts_home(request, event_id=None):
    event = get_object_or_404(Event, pk=event_id)

    if not request.user.has_perm('events.add_hosts', event):
        return HttpResponseForbidden('403 Forbidden')

    if request.is_ajax() and 'action' in request.POST:

        print request.POST

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

                    for perm in get_perms(host, event):
                        remove_perm(perm, host, event)

                    invite = Invitation.objects.get(user=host, event=event)

                    for perm in get_perms(host, invite):
                        remove_perm(perm, host, invite)

                    invite.delete()

                    return HttpResponse(json.dumps({'success': True, }))
                else:
                    errors.append('You can not remove your self from your own event')
        elif request.POST['action'] == 'add_host' and 'host' in request.POST:

            try:
                host = User.objects.get(username=request.POST['host'])
            except User.DoesNotExist:
                computer_errors.append('User does not exist')
            else:
                if host not in event.owner.all():
                    event.owner.add(host)

                    assign_perm('events.view_event', host, event)

                    if request.POST.get("can_edit_event_details", False) and \
                       request.POST.get("can_edit_event_details") == 'true':

                        assign_perm('events.change_event', host, event)

                    if request.POST.get("can_add_ticket_sales", False) and \
                       request.POST.get("can_add_ticket_sales") == 'true':

                        assign_perm('events.add_event_ticketsale', host, event)
                        assign_perm('events.change_event_ticketsale', host, event)
                        assign_perm('events.view_event_ticketsale', host, event)
                        assign_perm('events.delete_event_ticketsale', host, event)

                    if request.POST.get("can_edit_hosts", False) and \
                       request.POST.get("can_edit_hosts") == 'true':

                        assign_perm('events.search_hosts', host)
                        assign_perm('events.add_hosts', host, event)
                        assign_perm('events.change_hosts', host, event)
                        assign_perm('events.delete_hosts', host, event)
                        assign_perm('events.change_own_invitation', host)

                    send_new_event_email(request, host, event, request.user)

                    invite_profile = Invitation.objects.get(user=request.user, event=event)

                    profile = Invitation.objects.create(user=host, event=event, first_name=host.first_name,
                                                        last_name=host.last_name, email=host.email,
                                                        invited_by=invite_profile,
                                                        #available_sales=self.cleaned_data["available_sales"],
                                                        )

                    assign_perm('events.view_invitation', host, profile)

                    return HttpResponse(json.dumps({
                        'success': True,
                        'host': {
                            'name': host.get_full_name() if host.get_full_name() != '' else host.username,
                            'pk': host.pk,
                            'value': host.username
                        }
                    }))

        else:
            computer_errors.append('Invalid Action or not all required params are given.')

        return HttpResponse(json.dumps({'success': False, 'errors': errors, '_e': computer_errors}))

    context = {
        'section': 'hosts',
        'event': event,
        'events': get_events(request.user),
    }
    return render(request, 'events/hosts_home.html', context)

#==============================================================================
# Account Pages
#==============================================================================

@login_required
def accounts_home(request):
    context = {
        'events': get_events(request.user),
    }

    return render(request, 'accounts/accounts_home.html', context)


#==============================================================================
# Users Pages
#==============================================================================

@login_required
def users_home(request):
    if not request.user.has_perm('auth.add_user'):
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
    if not request.user.has_perm('auth.add_user'):
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
    if not request.user.has_perm('auth.add_user'):
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


@login_required
def users_edit_password(request, user_id=None):
    if not request.user.has_perm('auth.add_user'):
        return HttpResponseForbidden('403 Forbidden')

    user = get_object_or_404(User, pk=user_id)

    form = SetPasswordForm(user=user, data=request.POST or None, files=request.FILES or None)

    if form.is_valid():
        form.save()
        return redirect('users_edit', user_id=user_id)

    context = {
        'form': form,
        'ruser': user,
        'events': get_events(request.user),
    }

    return render(request, 'accounts/user_password_change.html', context)
