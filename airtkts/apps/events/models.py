from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Event(models.Model):
    slug = models.SlugField(blank=True)
    name = models.CharField(max_length=100)
    owner = models.ManyToManyField(User, related_name='owner')
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)

    def save(self, *args, **kwargs):

        # Convert Name of Event to Slug
        if self.slug == '':
            self.slug = slugify(unicode(self.name))

        super(Event, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.name


class TicketSale(models.Model):
    event = models.ForeignKey(Event)
    name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    minimum_ordered = models.PositiveIntegerField(default=1)
    maximum_ordered = models.PositiveIntegerField()
    show_remaining_count = models.BooleanField(default=False)

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


class Ticket(models.Model):
    sale = models.ForeignKey(TicketSale)
    purchase = models.ForeignKey(TicketOrder)
    validated = models.BooleanField(default=False)
    name = models.CharField(max_length=75)


class Invitation(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    user = models.ForeignKey(User, blank=True, null=True)

    event = models.ForeignKey(Event)
    available_sales = models.ManyToManyField(TicketSale)

    invited_by = models.ForeignKey('self', blank=True, null=True)
    max_guest_count = models.PositiveIntegerField(help_text='How many guests can this person invite?'
                                                   ' If they are not allowed to invite guests then set this to 0.')
    guests = models.ManyToManyField('self', blank=True, null=True)