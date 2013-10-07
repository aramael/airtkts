from django.contrib.auth.models import UserManager
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import int_to_base36
from django.template import loader
from django.contrib.sites.models import get_current_site
from django.core.mail import send_mail


def send_activation_email(request, user,
                          subject_template='email/activation_email_subject.txt',
                          email_template='email/activation_email.html',
                          extra_context=None):

    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain

    context = {
        'email': user.email,
        'domain': domain,
        'site_name': site_name,
        'uid': int_to_base36(user.pk),
        'user': user,
        'token': default_token_generator.make_token(user),
        'protocol': request.is_secure(),
    }

    if extra_context is not None:
        context.update(extra_context)
    subject = loader.render_to_string(subject_template, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string(email_template, context)
    send_mail(subject, email, None, [user.email])


def send_new_event_email(request, user, event, invited_by, subject_template='email/new_event_email_subject.txt',
                         email_template='email/new_event_email.html', extra_context=None):

    current_site = get_current_site(request)
    site_name = current_site.name
    domain = current_site.domain

    context = {
        'email': user.email,
        'domain': domain,
        'event': event,
        'invited_by': invited_by,
        'site_name': site_name,
        'user': user,
        'protocol': request.is_secure(),
    }

    if extra_context is not None:
        context.update(extra_context)
    subject = loader.render_to_string(subject_template, context)
    # Email subject *must not* contain newlines
    subject = ''.join(subject.splitlines())
    email = loader.render_to_string(email_template, context)
    send_mail(subject, email, None, [user.email])


class UserManager(UserManager):

    actions = ['delete_items', 'resend_activation_email', ]

    @property
    def bulk_actions(self):

        output_actions = []

        for action in self.actions:

            action_func = getattr(self, action)
            description = getattr(action_func, 'short_description', action.replace('_', ' '))

            output_actions.append({
                'action': action,
                'func': action_func,
                'description': description,
            })

        return output_actions

    def process_bulk_actions(self, request, action, queryset):
        if action in self.actions:
            function = getattr(self, action)
            return function(request, queryset)

    def delete_items(self, request, queryset):
        for item in queryset:
            item.delete()
    delete_items.short_description = 'Delete Selected Items'

    def resend_activation_email(self, request, queryset):
        """
        Re-sends activation emails for the selected users.

        Note that this will *only* send activation emails for users
        who are eligible to activate; emails will not be sent to users
        whose activation keys have expired or who have already
        activated.

        """

        for user in queryset:
            # Send out Email to Users
            send_activation_email(request, user)
    resend_activation_email.short_description = 'Resend Activation Email'