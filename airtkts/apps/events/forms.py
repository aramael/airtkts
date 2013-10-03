import stripe

from django.conf import settings
from django import forms
from .models import Event, TicketSale, TicketOrder, Ticket, Invitation
from airtkts.libs.forms import FieldsetsForm, ActionMethodForm, HideSlugForm
from django.db import transaction

stripe.api_key = settings.STRIPE_API_KEY


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
            return {"to": 'ticketsales_edit', 'event_id': instance.event.pk,'ticket_id': instance.pk}


class InviteForm(ActionMethodForm, FieldsetsForm, forms.ModelForm):

    POSSIBLE_ACTIONS = {'_save', '_addanother', '_continue'}

    class Meta:
        model = Invitation

    def __init__(self, *args, **kwargs):
        super(InviteForm, self).__init__(*args, **kwargs)

        if 'event' in self.fields:
            self.fields['event'].widget = forms.HiddenInput()

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'invites_home', 'event_id': instance.event.pk}
        elif action == '_addanother':
            return {"to": 'invites_new', 'event_id': instance.event.pk}
        elif action == '_continue':
            return {"to": 'invites_edit', 'event_id': instance.event.pk, 'invite_id': instance.pk}


class QuickInviteForm(ActionMethodForm, FieldsetsForm, forms.ModelForm):

    POSSIBLE_ACTIONS = {'_save', '_addanother', '_continue'}

    class Meta:
        model = Invitation
        exclude = ('guests')

    def __init__(self, *args, **kwargs):
        super(QuickInviteForm, self).__init__(*args, **kwargs)

        self.fields['event'].widget = forms.HiddenInput()
        self.fields['invited_by'].widget = forms.HiddenInput()

    def location_redirect(self, action, instance):
        if action == '_save':
            return {"to": 'invites_home', 'event_id': instance.event.pk}
        elif action == '_addanother':
            return {"to": 'invites_new', 'event_id': instance.event.pk}
        elif action == '_continue':
            return {"to": 'invites_edit', 'event_id': instance.event.pk, 'invite_id': instance.pk}


class TicketOfficeSaleForm(forms.Form):

    first_name = forms.CharField(max_length=50, required=True, label='First Name')
    last_name = forms.CharField(max_length=50, required=True, label='Last Name')
    email = forms.EmailField(required=True, label='Email Address')
    ticket_type = forms.HiddenInput()

    guest_invited = forms.BooleanField(required=False, label='I want to bring a +1 with me.')
    guest_first_name = forms.CharField(max_length=50, required=True, label='Guest\'s First Name')
    guest_last_name = forms.CharField(max_length=50, required=True, label='Guest\'s Last Name')
    guest_email = forms.EmailField(required=True, label='Guest\'s Email Address')
    guest_note = forms.CharField(widget=forms.Textarea, label='Do you want to add a note to your friend?')

    payment_method = forms.HiddenInput()
    stripe_token = forms.CharField(max_length=100)

    def save(self, event, *args, **kwargs):

        data = self.cleaned_data

        name = data['first_name'] + '' + data['last_name']

        # Creating TicketOrder

        order_kwargs = {
            'name': name,
            'email': data['email'],
            'payment_method': data['payment_method']
        }

        if data['stripe_token'] != '':

            customer = stripe.Customer.create(description=name, email=data['email'], card=data['stripe_token'])
            order_kwargs['customer'] = customer

        order = TicketOrder.objects.create(**order_kwargs)

        try:
            customer
        except NameError:
            pass
        else:
            ticket_price = 1200

            charge = stripe.Charge.create(amount=ticket_price, currency='usd',
                                          customer=customer.id, description='AIRTKTS ORDER: #' + order.pk)

            order.charge = charge.id
            order.save()

        ticket = Ticket.objects.create(name=name, purchase=order, sale='<TicketSale Object>')
    save = transaction.commit_on_success(save)
