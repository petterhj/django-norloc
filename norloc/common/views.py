# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals
from django.shortcuts import render


# View: Error
def error(request, message=None, status=400):
    # Render template  
    return render(request, 'error.html', {
        'message': message if message else ':(('
    }, status=status)


# View: Not found
def not_found(request, message=None):
    # Render template  
    return render(request, 'error.html', {
        'message': message if message else ':(( NOT FOUND'
    }, status=404)