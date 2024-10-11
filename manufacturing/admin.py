from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from manufacturing.models import Aircraft, Team, Part, Personnel, AircraftPart
from manufacturing.forms import AircraftPartAdminForm

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

# Register your models here.
admin.site.register(Aircraft, AircraftAdmin)
admin.site.register(Team)
admin.site.register(Part)
admin.site.register(Personnel)
admin.site.register(AircraftPart, AircraftPartAdmin)
