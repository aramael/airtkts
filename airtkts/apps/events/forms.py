from django import forms
from .models import Event
from airtkts.libs.forms import FieldsetsForm, ActionMethodForm, HideSlugForm


class EventForm(ActionMethodForm, HideSlugForm, FieldsetsForm, forms.ModelForm):

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