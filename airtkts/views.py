"""
Django views for airtkts project.

"""

from django.shortcuts import render


def home(request):
    """    Display the Landing Page    """

    context = {}

    return render(request, '', context)