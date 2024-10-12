from django import forms
from django.contrib.auth.models import User

from manufacturing.models import Part, Team, AircraftPart, Personnel


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



class PersonnelAdminForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True, help_text="Enter the username for the Personnel")
    password = forms.CharField(widget=forms.PasswordInput, required=True,
                               help_text="Enter the password for the Personnel")

    class Meta:
        model = Personnel
        fields = ['username', 'password', 'team', 'role']

    def save(self, commit=True):
        # Create a User instance with username and password
        user = User.objects.create_user(username=self.cleaned_data['username'], password=self.cleaned_data['password'])

        # Assign the User instance to Personnel before saving
        personnel = super().save(commit=False)
        personnel.user = user

        if commit:
            personnel.save()

        return personnel
