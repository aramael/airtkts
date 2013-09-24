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