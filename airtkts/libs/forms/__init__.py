from django import forms
from django.utils.datastructures import SortedDict
from django.forms.forms import BoundField


class ActionMethodForm(object):

    POSSIBLE_ACTIONS = None

    def clean(self):
        cleaned_data = super(ActionMethodForm, self).clean()

        # Check For Form Action
        if not self.POSSIBLE_ACTIONS.isdisjoint(cleaned_data):
            raise forms.ValidationError(
                'Invalid Action',
                code='invalid-action',
            )

        # Determine Form Action

        action = list(self.POSSIBLE_ACTIONS & set(self.data))

        if len(action) != 1:
            raise forms.ValidationError(
                'Multiple Actions Detected. Please Try Again',
                code='invalid-action',
            )

        cleaned_data['action'] = action[0]

        print cleaned_data

        return cleaned_data

    def save(self, *args, **kwargs):

        action = self.cleaned_data['action']

        del self.cleaned_data['action']

        instance = super(ActionMethodForm, self).save(*args, **kwargs)

        location_redirect = self.location_redirect(action, instance)

        return location_redirect

    def location_redirect(self, action, instance):

        raise NotImplementedError


class FieldsetsForm(object):

    @property
    def formatted_fieldset(self):

        if not hasattr(self, '_formatted_fieldset'):

            fieldsets = self.fieldsets

            formatted_fieldsets = []

            for fieldset in fieldsets:

                formatted_fieldset = {
                    'title': fieldset[0],
                    'classes': fieldset[1].get('classes', None),
                }

                fields = SortedDict()

                for field in fieldset[1].get('fields', []):
                    field_cls = self.fields.get(field, None)

                    fields[field] = BoundField(form=self, field=field_cls, name=field)

                formatted_fieldset['fields'] = fields

                formatted_fieldsets.append(formatted_fieldset)

            self._formatted_fieldset = formatted_fieldsets

        return self._formatted_fieldset


class HideOwnerForm(object):

    def __init__(self, *args, **kwargs):
        super(HideOwnerForm, self).__init__(*args, **kwargs)

        if 'owner' in self.fields:
            owner_field = 'owner'
        elif 'user' in self.fields:
            owner_field = 'user'

        self.fields[owner_field].widget = forms.HiddenInput()


class HideSlugForm(object):

    def __init__(self, *args, **kwargs):
        super(HideSlugForm, self).__init__(*args, **kwargs)

        if 'slug' in self.fields:
            self.fields['slug'].widget = forms.HiddenInput()