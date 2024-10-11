from django.contrib import admin
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart

class TeamAdmin(admin.ModelAdmin):
    filter_horizontal = ('parts',)

# Register your models here.
admin.site.register(Aircraft)
admin.site.register(Team, TeamAdmin)
admin.site.register(Part)
admin.site.register(Personnel)
admin.site.register(AircraftPart)
