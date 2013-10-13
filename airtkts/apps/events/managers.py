from django.db import models
from django.core.exceptions import ObjectDoesNotExist


class BulkActionsManager(object):

    actions = ['delete_items', ]

    MODEL_NAME = None

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
            if request.user.has_perm('events.delete_' + self.MODEL_NAME, item):
                item.delete()
    delete_items.short_description = 'Delete Selected Items'


class EventManager(BulkActionsManager, models.Manager):
    MODEL_NAME = 'event'


class TicketSaleManager(BulkActionsManager, models.Manager):
    MODEL_NAME = 'ticketsale'


class InvitationManager(BulkActionsManager, models.Manager):
    MODEL_NAME = 'invitation'

    actions = BulkActionsManager.actions + ['resend_invitation_email', ]

    def resend_invitation_email(self, request, queryset):
        for item in queryset:
            if request.user.has_perm('events.view_invitation', item):
                item.send_invitation_email(request)
    resend_invitation_email.short_description = 'Resend Invites'

    def serve_invite(self, *args, **kwargs):

        try:
            invite = self.get(*args, **kwargs)
        except ObjectDoesNotExist:
            return {'to': 'invite_invalid', 'invite': None}
        else:
            if invite.invitation_key_expired():
                return {'to': 'invite_expired', 'event_id': invite.event.pk, 'invite': invite}

            return {'to': 'ticket_office', 'event_id': invite.event.pk,
                    'event_slug': invite.event.slug, 'invite': invite}
