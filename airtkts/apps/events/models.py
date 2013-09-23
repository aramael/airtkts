from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    slug = models.SlugField()
    name = models.CharField(max_length=100)
    owner = models.ManyToManyField(User, related_name='owner')
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name