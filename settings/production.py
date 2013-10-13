import dj_database_url
import os
from settings.common import *

#==============================================================================
# Generic Django Project Settings
#==============================================================================

DEBUG = False
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': dj_database_url.config()
}

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/1.5/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ['.herokuapp.com']

# Make this unique, and don't share it with anybody.
# Set it by issuing following command
# <code>
# heroku config:add SECRET_KEY=''
# </code>
SECRET_KEY = os.environ['SECRET_KEY']

# Make this unique, and don't share it with anybody.
# Set it by issuing following command
# <code>
# heroku config:add STRIPE_PUBLISHABLE_KEY=''
# </code>
STRIPE_PUBLISHABLE_KEY = os.environ['STRIPE_PUBLISHABLE_KEY']

# Make this unique, and don't share it with anybody.
# Set it by issuing following command
# <code>
# heroku config:add STRIPE_API_KEY=''
# </code>
STRIPE_API_KEY = os.environ['STRIPE_API_KEY']