# Imports
from django.contrib import admin

from .models import Reference



# ModelAdmin: Reference
class ReferenceAdmin(admin.ModelAdmin):
    # List
    list_display = (
        'production', 'location',
        'title', 'date',
        # source
    )


# Models
admin.site.register(Reference, ReferenceAdmin)