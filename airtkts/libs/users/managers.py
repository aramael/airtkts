from django.contrib.auth.models import UserManager


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

    def delete_items(self, queryset):
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

        for profile in queryset:

            profile = profile.racallprofile

            profile = profile.resend_activation_email(request)
    resend_activation_email.short_description = 'Resend Activation Email'