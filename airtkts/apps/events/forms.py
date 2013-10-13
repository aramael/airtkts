import stripe
import logging
import json

from .models import Event, Invitation, Ticket, TicketOrder, TicketSale
from .helpers import get_available_sales
from airtkts.libs.forms import ActionMethodForm, FieldsetsForm, HideSlugForm
from airtkts.libs.users.managers import send_activation_email
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from django import forms
from guardian.shortcuts import assign_perm


# Get an instance of a logger
logger = logging.getLogger(__name__)

# Setup Stripe API
stripe.api_key = settings.STRIPE_API_KEY


class HostForm(ActionMethodForm, forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """

    POSSIBLE_ACTIONS = {'_save', '_addanother'}

    error_messages = {
        'duplicate_username': "An host with that UNI already exists.",
    }
    username = forms.RegexField(label="Columbia UNI", max_length=30,
                                regex=r'^[\w.@+-]+$',
                                help_text="Required. 30 characters or fewer. Letters, digits and "
                                          "@/./+/-/_ only.",
                                error_messages={
                                    'invalid': "This value may contain only letters, numbers and "
                                               "@/./+/-/_ characters."})

    first_name = forms.CharField()
    last_name = forms.CharField()

    can_edit_event_details = forms.BooleanField(required=False)
    can_add_ticket_sales = forms.BooleanField(required=False)
    can_edit_hosts = forms.BooleanField(required=False)

    max_guest_count = forms.IntegerField(help_text='How many guests can this person invite?'
                                                   ' If they are not allowed to invite guests then set this to 0.')
    class Meta:
        model = User
        fields = ('username', )

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        username = self.cleaned_data["username"]
        try:
            User._default_manager.get(username=username)
        except User.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def save(self, request,  event, commit=True):

        data = self.cleaned_data

        user = User.objects.create_user(username=data['username'])

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["username"] + "@columbia.edu"

        if commit:

            invite_profile = Invitation.objects.get(user=request.user, event=event)

            profile = Invitation.objects.create(user=user, event=event, first_name=user.first_name,
                                                last_name=user.last_name, email=user.email, invited_by=invite_profile,
                                                #available_sales=self.cleaned_data["available_sales"],
                                                max_guest_count=self.cleaned_data["max_guest_count"])

            user.save()
            event.owner.add(user)
            event.save()

            assign_perm('events.view_event', user, event)
            assign_perm('events.view_invitation', user, profile)

            if self.cleaned_data["can_edit_event_details"]:
                assign_perm('events.change_event', user, event)

            if self.cleaned_data["can_add_ticket_sales"]:
                assign_perm('events.add_event_ticketsale', user, event)
                assign_perm('events.change_event_ticketsale', user, event)
                assign_perm('events.view_event_ticketsale', user, event)
                assign_perm('events.delete_event_ticketsale', user, event)

            if self.cleaned_data["can_edit_hosts"]:
                assign_perm('events.search_hosts', user)
                assign_perm('events.add_hosts', user, event)
                assign_perm('events.change_hosts', user, event)
                assign_perm('events.delete_hosts', user, event)
                assign_perm('events.change_own_invitation', user)

            send_activation_email(request, user, subject_template='email/host_activation_subject.txt',
                                  email_template='email/host_activation_email.html',
                                  extra_context={'event': event, 'invited_by': invite_profile})
        return self.location_redirect(data['action'], event)
    save = transaction.commit_on_success(save)

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'hosts_home', 'event_id': instance.pk}
        elif action == '_addanother':
            return {"to": 'hosts_new', 'event_id': instance.pk}


class EventForm(ActionMethodForm, HideSlugForm, FieldsetsForm, forms.ModelForm):

    POSSIBLE_ACTIONS = {'_save', '_continue'}

    fieldsets = (
        (None, {
            'fields': ('name', 'description',)
        }),
        ("Location", {
            'fields': ('start_time', 'end_time', 'location',)
        }),
        ("Permissions", {
            'fields': ('owner',)
        }),
    )

    class Meta:
        model = Event

    def save(self, request, *args, **kwargs):
        action = self.cleaned_data['action']

        del self.cleaned_data['action']

        instance = super(ActionMethodForm, self).save(*args, **kwargs)

        owner_invite = Invitation.objects.create(user=request.user, event=instance, first_name=request.user.first_name,
                                                 last_name=request.user.last_name, email=request.user.email)
        assign_perm('events.change_invitation', request.user, owner_invite)

        for user in instance.owner.all():
            if user != request.user:
                invite = Invitation.objects.create(user=user, event=instance, first_name=user.first_name,
                                                   last_name=user.last_name, email=user.email, invited_by=owner_invite)

                assign_perm('events.change_invitation', user, invite)

            assign_perm('events.view_event', user, instance)
            assign_perm('events.change_event', user, instance)

            assign_perm('events.add_event_ticketsale', user, instance)
            assign_perm('events.change_event_ticketsale', user, instance)
            assign_perm('events.view_event_ticketsale', user, instance)
            assign_perm('events.delete_event_ticketsale', user, instance)

            assign_perm('events.search_hosts', user)
            assign_perm('events.add_hosts', user, instance)
            assign_perm('events.change_hosts', user, instance)
            assign_perm('events.delete_hosts', user, instance)

        location_redirect = self.location_redirect(action, instance)

        return location_redirect

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'event_home'}
        elif action == '_continue':
            return {"to": 'ticketsales_new', 'event_id': instance.pk}


class TicketSaleForm(ActionMethodForm, FieldsetsForm, forms.ModelForm):

    POSSIBLE_ACTIONS = {'_save', '_addanother', '_continue'}

    fieldsets = (
        (None, {
            'fields': ('name', 'price', 'quantity',)
        }),
        ('Purchase Options', {
            'fields': ('start_time', 'end_time', 'minimum_ordered','maximum_ordered')
        }),
    )

    class Meta:
        model = TicketSale

    def __init__(self, *args, **kwargs):
        super(TicketSaleForm, self).__init__(*args, **kwargs)

        if 'event' in self.fields:
            self.fields['event'].widget = forms.HiddenInput()

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'ticketsales_home', 'event_id': instance.event.pk}
        elif action == '_addanother':
            return {"to": 'ticketsales_new', 'event_id': instance.event.pk}
        elif action == '_continue':
            return {"to": 'ticketsales_edit', 'event_id': instance.event.pk, 'ticket_id': instance.pk}


class InviteForm(ActionMethodForm, FieldsetsForm, forms.ModelForm):

    POSSIBLE_ACTIONS = {'_save', '_addanother', '_continue'}

    class Meta:
        model = Invitation
        exclude = ['ticket_order', 'invite_key']

    def __init__(self, event, user, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)

        if 'event' in self.fields:
            self.fields['event'].widget = forms.HiddenInput()
        if 'invited_by' in self.fields and not user.has_perm('events.change_hosts', event):
            self.fields['invited_by'].widget = forms.HiddenInput()
        if 'available_sales' in self.fields:
            self.fields['available_sales'].queryset = get_available_sales(self.initial.get('invited_by', None))
            self.fields['available_sales'].initial = get_available_sales(self.initial.get('invited_by', None))

    def save(self, request, invite, *args, **kwargs):

        redirect = super(InviteForm, self).save(*args, **kwargs)

        instance = redirect['instance']

        if type(instance.invited_by.user) is User:
            assign_perm('events.view_invitation', instance.invited_by.user, instance)

        instance.send_invitation_email(request)

        invite.guests.add(instance)
        invite.save()

        del redirect['instance']

        return redirect

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'invites_home', 'event_id': instance.event.pk, 'instance': instance}
        elif action == '_addanother':
            return {"to": 'invites_new', 'event_id': instance.event.pk, 'instance': instance}
        elif action == '_continue':
            return {"to": 'invites_edit', 'event_id': instance.event.pk, 'invite_id': instance.pk, 'instance': instance}


class QuickInviteForm(InviteForm):

    class Meta(InviteForm.Meta):
        exclude = InviteForm.Meta.exclude + ['guests', 'rsvp_status']


class LimitedInviteForm(InviteForm):

    class Meta(InviteForm.Meta):
        exclude = InviteForm.Meta.exclude + ['guests', 'max_guest_count', 'invited_by', 'event',
                                             'available_sales', 'user', 'rsvp_status']


class GuestInviteForm(InviteForm):

    class Meta(InviteForm.Meta):
        exclude = InviteForm.Meta.exclude + ['guests', 'invited_by', 'event']


class TicketOfficeSaleForm(forms.Form):

    CREDIT_CARD_ERRORS = {
        'incorrect_number': '',
        'invalid_number': 'It seems that you have mistyped your credit card number. Can you try typing it again?',
        'invalid_expiry_month': 'We think you\'ve mistyped the expiration month. Try copying it again.',
        'invalid_expiry_year': 'You may have mistyped the expiration year, maybe try copying it again.',
        'invalid_cvc': 'The CVC code, the three-digit card security code printed on the back signature panel of '
                       'the card or the four-digit code printed on the front side of the card above the number if '
                       'you have American Express, seems to be invalid. Please try typing it again.',
        'expired_card': 'The card that you entered is expired. Please try using a different card.',
        'incorrect_cvc': 'The CVC code, the three-digit card security code printed on the back signature panel of '
                         'the card or the four-digit code printed on the front side of the card above the number if '
                         'you have American Express, seems to be incorrect. Please try typing it again.',
        'incorrect_zip': 'You have provided the wrong ZIP code for the credit card. Remember this ZIP code is '
                         'not the ZIP code of where you currently live or reside; however, it is the ZIP code that '
                         'the credit card is registered under with your bank. Try typing it again.',
        'card_declined': 'The you supplied was declined. Try submitting it again, if it doesn\'t work again then try '
                         'calling your bank to see if there is an issue you need to resolve. You\'re bank\'s number '
                         'is on the back of you\'re card.',
        'processing_error': 'An error occurred while trying to process your card. Please try submitting again.',
    }

    rsvp = forms.CharField(max_length=12)

    first_name = forms.CharField(max_length=50, required=True, label='First Name')
    last_name = forms.CharField(max_length=50, required=True, label='Last Name')
    email = forms.EmailField(required=True, label='Email Address')
    ticket_type = forms.CharField(max_length=50, widget=forms.HiddenInput, required=False)

    guest_invited = forms.BooleanField(required=False, label='I want to bring a +1 with me.')
    guest_first_name = forms.CharField(max_length=50, required=False, label='Guest\'s First Name')
    guest_last_name = forms.CharField(max_length=50, required=False, label='Guest\'s Last Name')
    guest_email = forms.EmailField(required=False, label='Guest\'s Email Address')
    guest_note = forms.CharField(widget=forms.Textarea, required=False, label='Do you want to add a note to your friend?')

    payment_method = forms.CharField(max_length=50, widget=forms.HiddenInput, required=False)
    stripe_token = forms.CharField(max_length=100, required=False, widget=forms.HiddenInput)

    def __init__(self, request, invite, event, *args, **kwargs):
        self.request = request
        self.invite = invite
        self.event = event

        super(TicketOfficeSaleForm, self).__init__(*args, **kwargs)

    def clean_ticket_type(self):

        data = self.cleaned_data['ticket_type']

        if self.cleaned_data['rsvp'] != Invitation.DECLINED:

            try:
                ticket_sale = self.invite.available_sales.get(slug=data, event=self.event)
            except TicketSale.DoesNotExist:
                raise forms.ValidationError("Unfortunately we were unable "
                                            "to locate the ticket type `%(ticket_type)` that you requested. ",
                                            code=TicketSale.INVALID, params={'ticket_type': data})
            else:
                if not ticket_sale.has_tickets_remaining():
                    raise forms.ValidationError("It seems we are all sold out of that type of ticket `%(ticket_type)`. "
                                                "Our sincerest apologies, please try selecting another ticket type",
                                                code=TicketSale.SOLD_OUT, params={'ticket_type': data})

            return ticket_sale

        return data

    def clean(self):
        """
        The clean method will authorise a charge but not charge it in case
        another error is thrown. If it fails, it simply raises the error
        given from Stripe's library as a standard ValidationError for proper
         feedback however it is converted into a more friendly message by
         the ``CREDIT_CARD_ERRORS`` dictionary.
        """

        data = super(TicketOfficeSaleForm, self).clean()

        if not self.errors and data['rsvp'] == Invitation.ATTENDING:

            ticket_sale = data['ticket_type']

            if data['stripe_token'] is not None:

                invitee_full_name = data['first_name'] + ' ' + data['last_name']

                try:
                    # Credit Card Processing
                    customer = stripe.Customer.create(description=invitee_full_name,
                                                      email=data['email'], card=data['stripe_token'])

                    data['stripe_customer'] = customer.id

                    # Authorize the Charge but DO NOT CHARGE in case there is an error
                    charge = stripe.Charge.create(amount=ticket_sale.price*100, currency='usd',
                                                  capture=False, customer=customer.id)

                    data['stripe_charge'] = charge.id

                except stripe.CardError, e:
                    # Since it's a decline, stripe.CardError will be caught
                    body = e.json_body
                    err = body['error']

                    if err['type'] == 'card_error':

                        error = [self.CREDIT_CARD_ERRORS.get(err['code'], self.CREDIT_CARD_ERRORS['processing_error'])]
                        self._errors["stripe_token"] = self.error_class(error)
                except stripe.AuthenticationError, e:
                    # Authentication with Stripe's API failed
                    # (maybe you changed API keys recently)
                    logger.critical('Stripe Authentication Failed. ' + str(e.json_body))
                else:
                    data['payment_method'] = TicketOrder.CREDIT_CARD
                    data['balance'] = 0
            else:
                # Wait for Event Date @ Door
                data['payment_method'] = TicketOrder.CASH
                data['balance'] = -ticket_sale.price

            del data['stripe_token']

        return data

    def save(self, *args, **kwargs):

        data = self.cleaned_data

        if data['rsvp'] == Invitation.DECLINED:
            self.invite.rsvp_status = Invitation.DECLINED
            self.invite.save()
            return json.dumps({'success': True, })

        invitee_full_name = data['first_name'] + ' ' + data['last_name']

        # Creating TicketOrder

        order_kwargs = {
            'name': invitee_full_name,
            'email': data['email'],
            'payment_method': data['payment_method'],
            'balance': data['balance'],
        }

        order = TicketOrder.objects.create(**order_kwargs)

        ticket_sale = data['ticket_type']

        # Payment Methods

        if 'stripe_customer' in data:
            order.customer = data['stripe_customer']
        if 'stripe_charge' in data:
            order.charge = data['stripe_charge']

            # Capture the Pre-Authorised Card
            ch = stripe.Charge.retrieve(data['stripe_charge'])
            ch.capture()

        ticket = Ticket.objects.create(name=invitee_full_name, purchase=order, sale=ticket_sale)

        if self.invite.can_bring_guests() and 'guest_email' in data and data['guest_email'] != '':
            guest = Invitation.objects.create(event=self.event, first_name=data['guest_first_name'],
                                              last_name=data['guest_last_name'], email=data['guest_email'],
                                              invited_by=self.invite, max_guest_count=0)

            guest.available_sales = self.invite.available_sales.all()
            guest.save()
            guest.invitation_email_message(request=self.request, note=data['guest_note'])

            self.invite.guests.add(guest)

        order.save()
        self.invite.ticket_order = order
        self.invite.rsvp_status = Invitation.ATTENDING
        self.invite.mark_used()
        self.invite.save()

        return {'to': 'order_confirmation', 'order_id': order.pk}

    save = transaction.commit_on_success(save)
