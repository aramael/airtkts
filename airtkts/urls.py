from django.conf.urls import patterns, include, url
from django.contrib.auth import views as auth_views

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', 'airtkts.views.home', name='home'),
    url(r'^event/(?P<event_id>[0-9]+)/(?P<event_slug>\w+)', 'airtkts.views.ticket_office', name='ticket_office'),

    # Account Home
    url(r'^accounts/$', 'airtkts.views.accounts_home', name='accounts_home'),

    # User Pages
    url(r'^accounts/users/$', 'airtkts.views.users_home', name='users_home'),
    url(r'^accounts/users/new$', 'airtkts.views.users_new', name='users_new'),
    url(r'^accounts/users/(?P<user_id>[0-9]+)/$', 'airtkts.views.users_edit', name='users_edit'),
    url(r'^accounts/users/me/$', 'airtkts.views.users_edit', {'self_edit': True}, name='account_edit'),

    # Account Event Pages
    url(r'^accounts/event/$', 'airtkts.views.event_home', name='event_home'),
    url(r'^accounts/event/new/$', 'airtkts.views.event_form', name='event_new'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/$', 'airtkts.views.event_dashboard', name='event_dashboard'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/edit/$', 'airtkts.views.event_form', name='event_edit'),

    url(r'^accounts/event/(?P<event_id>[0-9]+)/hosts/$', 'airtkts.views.hosts_home', name='hosts_home'),
    #url(r'^accounts/event/(?P<event_id>[0-9]+)/hosts/new/$', 'airtkts.views.hosts_new', name='hosts_new'),

    # Ticket Sales
    url(r'^accounts/event/(?P<event_id>[0-9]+)/tickets/$', 'airtkts.views.ticketsales_home', name='ticketsales_home'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/tickets/(?P<ticket_id>[0-9]+)/$', 'airtkts.views.ticketsales_form',
        name='ticketsales_edit'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/tickets/new/$', 'airtkts.views.ticketsales_form', name='ticketsales_new'),

    # Invites
    url(r'^accounts/event/(?P<event_id>[0-9]+)/invites/$', 'airtkts.views.invites_home', name='invites_home'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/invites/(?P<invite_id>[0-9]+)/$', 'airtkts.views.invites_form',
        name='invites_edit'),
    url(r'^accounts/event/(?P<event_id>[0-9]+)/invites/new/$', 'airtkts.views.invites_form', name='invites_new'),

    url(r'^admin/', include(admin.site.urls)),

    # Account Pages
    url(r'^accounts/login/$',
       auth_views.login,
       {'template_name': 'auth/login.html'},
       name='auth_login'),
    url(r'^accounts/logout/$',
       auth_views.logout,
       {'template_name': 'auth/logout.html'},
       name='auth_logout'),
    url(r'^accounts/password/change/$',
       auth_views.password_change,
        {'template_name': 'auth/password_change_form.html'},
       name='auth_password_change'),
    url(r'^accounts/password/change/done/$',
       auth_views.password_change_done,
       {'template_name': 'auth/password_change_done.html'},
       name='auth_password_change_done'),
    url(r'^accounts/password/reset/$',
       auth_views.password_reset,
       {'template_name': 'auth/password_reset_form.html',
        'email_template_name': 'auth/password_reset_email.html'},
       name='auth_password_reset'),
    url(r'^accounts/password/reset/confirm/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)/$',
       auth_views.password_reset_confirm,
       {'template_name': 'auth/password_reset_confirm.html'},
       name='accounts/auth_password_reset_confirm'),
    url(r'^password/reset/complete/$',
       auth_views.password_reset_complete,
       {'template_name': 'auth/password_reset_complete.html'},
       name='accounts/auth_password_reset_complete'),
    url(r'^accounts/password/reset/done/$',
       auth_views.password_reset_done,
       {'template_name': 'auth/password_reset_done.html'},
       name='auth_password_reset_done'),
)