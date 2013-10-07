from django.db import models


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