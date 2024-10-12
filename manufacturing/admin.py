from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart
from manufacturing.forms import AircraftPartAdminForm, PersonnelAdminForm


class AircraftPartAdmin(admin.ModelAdmin):
    """
    Admin interface for managing AircraftPart objects.
    Handles validations and messages related to part assignments.
    """
    form = AircraftPartAdminForm  # Specify the form for AircraftPart

    def save_model(self, request, obj, form, change):
        """
        Override save_model to check for existing assignments before saving.
        """
        # Check if this part is already assigned to this specific aircraft
        if AircraftPart.objects.filter(part=obj.part, aircraft=obj.aircraft).exists():
            self.message_user(request, _("This part is already assigned to this aircraft."), level='error')
            return

        # Check if the part is assigned to a different aircraft
        if AircraftPart.objects.filter(part=obj.part).exclude(aircraft=obj.aircraft).exists():
            self.message_user(request, _("This part is already assigned to another aircraft."), level='error')
            return

        super().save_model(request, obj, form, change)  # Call the superclass method to save the object
        self.message_user(request, _("The aircraft part was added successfully."), level='success')


class AircraftPartInline(admin.TabularInline):
    """
    Inline for displaying AircraftPart associations within the Aircraft admin.
    """
    model = AircraftPart
    extra = 1  # Number of empty forms to display
    can_delete = True  # Allow deletion of inline objects


class AircraftAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Aircraft objects.
    Displays AircraftPart associations inline.
    """
    inlines = [AircraftPartInline]
    list_display = ('name', 'serial_number', 'created_at', 'is_produced')  # Fields to display in the list
    readonly_fields = ('is_produced',)  # Make is_produced read-only


class PersonnelAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Personnel objects.
    """
    form = PersonnelAdminForm
    list_display = ['user', 'team', 'role']  # Fields to display in the list
    search_fields = ['user__username', 'team__name', 'role']  # Fields to search


class PartAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Part objects.
    Provides filters based on the user's permissions.
    """
    list_display = ['name', 'aircraft_type', 'is_used', 'get_responsible_teams']
    search_fields = ['name', 'aircraft_type']
    readonly_fields = ['is_used']

    def get_queryset(self, request):
        """
        Customize the queryset to filter parts based on the user's team permissions.
        """
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
        return qs.none()  # Return empty queryset if no team

    def has_change_permission(self, request, obj=None):
        """
        Check if the user has permission to change a part.
        """
        if request.user.is_superuser:
            return True
        personnel = Personnel.objects.get(user=request.user)
        return obj and personnel.team.can_produce_part(obj)

    def has_delete_permission(self, request, obj=None):
        """
        Check if the user has permission to delete a part.
        """
        if request.user.is_superuser:
            return True
        personnel = Personnel.objects.get(user=request.user)
        return obj and personnel.team.can_produce_part(obj)

    def get_responsible_teams(self, obj):
        """
        List the teams that are allowed to produce this part.
        """
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

    get_responsible_teams.short_description = 'Responsible Teams'  # Column header for responsible teams


class PersonnelInline(admin.TabularInline):
    """
    Inline for displaying Personnel associated with a Team in the Team admin.
    """
    model = Personnel
    extra = 0  # No extra empty forms
    can_delete = False  # Disable deletion of inlined personnel


class TeamAdmin(admin.ModelAdmin):
    """
    Admin interface for managing Team objects.
    """
    list_display = ['name', 'description']  # Fields to display
    readonly_fields = ['name', 'description']  # Make these fields read-only
    inlines = [PersonnelInline]  # Show associated personnel inline

    def has_add_permission(self, request, obj=None):
        """
        Disable the add permission for Team.
        """
        return False

    def has_delete_permission(self, request, obj=None):
        """
        Disable the delete permission for Team.
        """
        return False


# Register your models here.
admin.site.register(Aircraft, AircraftAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(Personnel, PersonnelAdmin)
admin.site.register(AircraftPart, AircraftPartAdmin)
