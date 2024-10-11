from django import forms

from manufacturing.models import Part, Team, AircraftPart


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name']  # Assuming you have a field to choose the teams

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit teams to those that can produce this part
        self.fields['teams'].queryset = Team.objects.filter(parts=self.instance)



class PartModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        # Check if this part is already used in any aircraft
        if AircraftPart.objects.filter(part=obj).exists():
            return f"{obj.name} (already used)"
        return obj.name



class AircraftPartAdminForm(forms.ModelForm):
    part = PartModelChoiceField(queryset=Part.objects.all(), required=True)

    class Meta:
        model = AircraftPart
        fields = '__all__'
