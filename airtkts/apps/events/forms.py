from django import forms
from .models import Event
from airtkts.libs.forms import FieldsetsForm, ActionMethodForm, HideSlugForm


class EventForm(ActionMethodForm, HideSlugForm, FieldsetsForm, forms.ModelForm):

    POSSIBLE_ACTIONS = {'_save', '_addanother', '_continue'}

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
        elif action == '_addanother':
            return {"to": 'event_new'}
        elif action == '_continue':
            return {"to": 'event_edit', 'event_id': instance.pk, 'event_slug':instance.slug}