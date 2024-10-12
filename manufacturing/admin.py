from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart
from manufacturing.forms import AircraftPartAdminForm, PersonnelAdminForm


class AircraftPartAdmin(admin.ModelAdmin):
    form = AircraftPartAdminForm  # Specify the form

    def save_model(self, request, obj, form, change):
        # Check if this part is already assigned to this specific aircraft
        if AircraftPart.objects.filter(part=obj.part, aircraft=obj.aircraft).exists():
            self.message_user(request, _("This part is already assigned to this aircraft."), level='error')
            return

        # Check if the part is assigned to a different aircraft
        if AircraftPart.objects.filter(part=obj.part).exclude(aircraft=obj.aircraft).exists():
            self.message_user(request, _("This part is already assigned to another aircraft."), level='error')
            return

        super().save_model(request, obj, form, change)
        self.message_user(request, _("The aircraft part was added successfully."), level='success')

class AircraftPartInline(admin.TabularInline):
    model = AircraftPart
    extra = 1
    can_delete = True

class AircraftAdmin(admin.ModelAdmin):
    inlines = [AircraftPartInline]
    list_display = ('name', 'serial_number', 'created_at', 'is_produced')
    readonly_fields = ('is_produced',)

class PersonnelAdmin(admin.ModelAdmin):
    form = PersonnelAdminForm
    list_display = ['user', 'team', 'role']
    search_fields = ['user__username', 'team__name', 'role']

class PartAdmin(admin.ModelAdmin):
    list_display = ['name', 'aircraft_type', 'is_used', 'get_responsible_teams']
    search_fields = ['name', 'aircraft_type']
    readonly_fields = ['is_used']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Only show parts based on the user's team permissions
        personnel = Personnel.objects.filter(user=request.user).first()
        if personnel:
            team = personnel.team
            return qs.filter(name__in=[Part.WING if team.name == Team.WING_TEAM else '',
                                       Part.BODY if team.name == Team.BODY_TEAM else '',
                                       Part.TAIL if team.name == Team.TAIL_TEAM else '',
                                       Part.AVIONICS if team.name == Team.AVIONICS_TEAM else ''])
        return qs.none()

    def has_change_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        personnel = Personnel.objects.get(user=request.user)
        return obj and personnel.team.can_produce_part(obj)

    def has_delete_permission(self, request, obj=None):
        if request.user.is_superuser:
            return True
        personnel = Personnel.objects.get(user=request.user)
        return obj and personnel.team.can_produce_part(obj)

    def get_responsible_teams(self, obj):
        # List the teams that are allowed to produce this part
        responsible_teams = []
        if obj.name == Part.WING:
            responsible_teams.append(Team.WING_TEAM)
        if obj.name == Part.BODY:
            responsible_teams.append(Team.BODY_TEAM)
        if obj.name == Part.TAIL:
            responsible_teams.append(Team.TAIL_TEAM)
        if obj.name == Part.AVIONICS:
            responsible_teams.append(Team.AVIONICS_TEAM)

        return ", ".join(responsible_teams)

    get_responsible_teams.short_description = 'Responsible Teams'

class PersonnelInline(admin.TabularInline):
    model = Personnel
    extra = 0
    can_delete = False

class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    readonly_fields = ['name', 'description']
    inlines = [PersonnelInline]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# Register your models here.
admin.site.register(Aircraft, AircraftAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Personnel, PersonnelAdmin)
admin.site.register(AircraftPart, AircraftPartAdmin)
