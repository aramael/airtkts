#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":

    ENVIRONMENT = os.getenv('ENVIRONMENT')

    if ENVIRONMENT == 'STAGING':
        settings = 'staging'
    elif ENVIRONMENT == 'PRODUCTION':
        settings = 'production'
    else:
        settings = 'local'

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings.{settings}".format(settings=settings))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
