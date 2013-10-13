from django.contrib import admin
from .models import TicketOrder, Ticket, Invitation

admin.site.register(TicketOrder)
admin.site.register(Ticket)
admin.site.register(Invitation)