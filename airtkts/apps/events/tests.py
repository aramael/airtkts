from django.test import TestCase
from django.contrib.auth.models import User
from .models import Event
from datetime import timedelta
from django.utils.timezone import now


class EventTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user('events_test', 'events_test@test.com', 'password')

        # Create 1st Test Event
        event1 = Event(slug='', name='Event #1', description='some even better event', start_time=now(),
                       end_time=now() + timedelta(hours=2), location='')
        event1.save()
        event1.owner.add(user)

        # Create 2nd Test Event
        event2 = Event(slug='event-two', name='Event #2', description='some awesome event', start_time=now(),
                       end_time=now() + timedelta(hours=2), location='')
        event2.save()
        event2.owner.add(user)

    def test_event_can_slugify(self):
        event1 = Event.objects.get(name="Event #1")
        event2 = Event.objects.get(name="Event #2")
        self.assertEqual(event1.slug, 'event-1')
        self.assertEqual(event2.slug, 'event-two')