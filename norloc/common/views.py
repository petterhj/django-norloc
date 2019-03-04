# -*- coding: utf-8 -*-

# Imports
from __future__ import unicode_literals
from django.shortcuts import render


# View: Error
def error(request, title=None, message=None, status=400):
    # Render template  
    return render(request, 'error.html', {
        'title': title,
        'message': message,
        'status_code': status
    }, status=status)


# View: Not found
def not_found(request, title=None, message=None):
    # Render template  
    return error(request, 'Side ikke funnet', message, status=404)