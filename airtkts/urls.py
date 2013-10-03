from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'airtkts.views.home', name='home'),
    url(r'^event/(?P<event_id>[0-9]+)/(?P<event_slug>\w+)', 'airtkts.views.ticket_office', name='ticket_office'),

    # Account Event Pages
    url(r'^accounts/event/$', 'airtkts.views.event_home', name='event_home'),
    url(r'^accounts/event/new/$', 'airtkts.views.event_form', name='event_new'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/$', 'airtkts.views.event_dashboard', name='event_dashboard'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/edit/$', 'airtkts.views.event_form', name='event_edit'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/tickets/$', 'airtkts.views.ticketsales_home', name='ticketsales_home'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/tickets/(?P<ticket_id>[0-9]+)/$', 'airtkts.views.ticketsales_form',
        name='ticketsales_edit'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/tickets/new/$', 'airtkts.views.ticketsales_form', name='ticketsales_new'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/invites/$', 'airtkts.views.invites_home', name='invites_home'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/invites/(?P<invite_id>[0-9]+)/$', 'airtkts.views.invites_form',
        name='invites_edit'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/invites/new/$', 'airtkts.views.invites_form', name='invites_new'),

    url(r'^admin/', include(admin.site.urls)),
)