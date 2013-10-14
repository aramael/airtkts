import datetime
import hashlib
import random
import re

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.text import slugify
from .managers import EventManager, TicketSaleManager, InvitationManager

try:
    from django.utils.timezone import now as datetime_now
except ImportError:
    datetime_now = datetime.datetime.now

SHA1_RE = re.compile('^[a-f0-9]{40}$')


class Event(models.Model):
    slug = models.SlugField(blank=True)
    name = models.CharField(max_length=100)
    owner = models.ManyToManyField(User, related_name='owner')
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)

    objects = EventManager()

    class Meta:
        permissions = (
            ('view_event', 'Can view event'),
            ('search_hosts', 'Can search event hosts'),
            ('add_hosts', 'Can add event hosts'),
            ('change_hosts', 'Can edit event hosts'),
            ('delete_hosts', 'Can delete event hosts'),
            ('view_event_ticketsale', 'Can view event ticket sale'),
            ('add_event_ticketsale', 'Can add event ticket sale'),
            ('change_event_ticketsale', 'Can edit event ticket sale'),
            ('delete_event_ticketsale', 'Can delete event ticket sale'),
        )

    def save(self, *args, **kwargs):
        # Convert Name of Event to Slug
        if self.slug == '':
            self.slug = slugify(unicode(self.name))

        super(Event, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class TicketSale(models.Model):

    INVALID = 400
    SOLD_OUT = 500

    slug = models.SlugField(blank=True, null=True, default=None)
    icon_name = models.CharField(max_length=25, default='ticket', null=True)
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=100)
    description = models.TextField(default='', blank=True)
    quantity = models.IntegerField()
    price = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    minimum_ordered = models.PositiveIntegerField(default=1)
    maximum_ordered = models.PositiveIntegerField()
    show_remaining_count = models.BooleanField(default=False)

    objects = TicketSaleManager()

    class Meta:
        permissions = (
            ('view_ticketsale', 'Can view ticket sale'),
        )

    def save(self, *args, **kwargs):
        # Convert Name of Event to Slug
        if self.slug == '':
            self.slug = slugify(unicode(self.name))

        super(TicketSale, self).save(*args, **kwargs)

    def has_tickets_remaining(self):
        return True

    def __unicode__(self):
        return "{event}: {name}".format(name=self.name, event=self.event.name)


class TicketOrder(models.Model):
    CREDIT_CARD = 'cc'
    CASH = 'cash'

    PAYMENT_METHODS = (
        (CASH, 'Cash'),
        (CREDIT_CARD, 'Credit Card')
    )

    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default=CREDIT_CARD)
    customer = models.CharField(max_length=50, blank=True, null=True)
    charge = models.CharField(max_length=100, blank=True, null=True)
    purchase_time = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    balance = models.DecimalField(decimal_places=2, max_digits=8, default=0)


class Ticket(models.Model):
    sale = models.ForeignKey(TicketSale)
    purchase = models.ForeignKey(TicketOrder)
    validated = models.BooleanField(default=False)
    name = models.CharField(max_length=75)


class Invitation(models.Model):
    USED_INVITE_KEY = 'ALREADY_BOUGHT_TICKETS'

    NO_ANSWER = '--'
    ATTENDING = 'ATTENDING'
    DECLINED = 'DECLINED'

    RSVP_CHOICES = (
        (NO_ANSWER, '--'),
        (ATTENDING, 'Attending'),
        (DECLINED, 'Decline'),
    )

    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    user = models.ForeignKey(User, blank=True, null=True)

    event = models.ForeignKey(Event)
    available_sales = models.ManyToManyField(TicketSale, blank=True, null=True)

    invited_by = models.ForeignKey('self', blank=True, null=True)
    max_guest_count = models.PositiveIntegerField(help_text='How many guests can this person invite? If '
                                                            'they are not allowed to invite guests then set this to 0.',
                                                  null=True, blank=True)
    guests = models.ManyToManyField('self', blank=True, null=True)

    invite_key = models.CharField(max_length=40, default='', blank=True, null=True)
    rsvp_status = models.CharField(choices=RSVP_CHOICES, default=NO_ANSWER, max_length=12)
    ticket_order = models.ForeignKey(TicketOrder, default=None, blank=True, null=True)

    objects = InvitationManager()

    class Meta:
        permissions = (
            ('view_invitation', 'Can view invitation'),
            ('change_own_invitation', 'Can change own invitation'),
        )

    def save(self, *args, **kwargs):

        if self.invite_key == '':

                salt = hashlib.sha1(str(random.random())).hexdigest()[:5]
                username = self.email
                if isinstance(username, unicode):
                    username = username.encode('utf-8')
                invite_key = hashlib.sha1(salt+username).hexdigest()

                self.invite_key = invite_key

        return super(Invitation, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.first_name + ' ' + self.last_name

    def can_bring_guests(self):
        """
        Determine whether this ``Invitation`` can bring a guest
        """
        return self.max_guest_count > 0 and self.max_guest_count > self.guests.all().count()

    def mark_used(self):
        """
        Mark this ``Invitation``'s invite key as expired
        """

        self.invite_key = self.USED_INVITE_KEY
        self.save()

    def invitation_key_expired(self):
        """
        Determine whether this ``Invitation``'s invite
        key has expired, returning a boolean -- ``True`` if the key
        has expired.

        Key expiration is determined by a two-step process:

        1. If the user has already bought a ticket, the key will have been
           reset to the string constant ``USED_INVITE_KEY``. Reusing an invite
           is not permitted, and so this method returns ``True`` in
           this case.

        2. Otherwise, it checks if the event has already passed and
           therefore the key has expired and this method returns ``True``.

        """
        return self.invite_key == self.USED_INVITE_KEY or (self.event.start_time <= datetime_now())

    invitation_key_expired.boolean = True

    def mail_guest(self, subject, body):
        msg = EmailMultiAlternatives(subject, '', None, [self.email, ])
        msg.attach_alternative(body, "text/html")
        msg.track_opens = True
        msg.track_clicks = True
        msg.auto_text = True
        msg.send()

    def invitation_email_message(self, request, note=None, subject_template='email/invite_email_subject.txt',
                                 email_template='email/invite_email.html', extra_context=None):

        current_site = get_current_site(request)
        site_name = current_site.name
        domain = current_site.domain

        context = {
            'email': self.email,
            'domain': domain,
            'event': self.event,
            'invited_by': self.invited_by,
            'site_name': site_name,
            'user': self,
            'note': note,
            'mailing_address': 'airTKTS <br/> 5980 Lerner Hall <br/>2920 Broadway <br/>New York, NY 10027',
            'protocol': 'https' if request.is_secure() else 'http',
        }

        if extra_context is not None:
            context.update(extra_context)
        subject = loader.render_to_string(subject_template, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())

        context.update({'subject': subject})

        email = loader.render_to_string(email_template, context)

        return subject, email

    def send_invitation_email(self, *args, **kwargs):
        """
        Send out an email to the holder of this ``Invitation`` reminding
        them to purchase a ticket to the event in question. Only sends
        out if the user's invite key is still valid
        """

        if not self.invitation_key_expired():
            subject, email = self.invitation_email_message(*args, **kwargs)
            self.mail_guest(subject, email)