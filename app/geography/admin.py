from django.contrib import admin
from geography.models import Region


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    pass
