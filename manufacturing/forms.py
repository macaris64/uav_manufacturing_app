from django import forms
from django.contrib.auth.models import User

from manufacturing.models import Part, Team, AircraftPart, Personnel


class PartForm(forms.ModelForm):
    """
    Form for creating or updating Part objects.
    Only the name field is included for the Part model.
    """
    class Meta:
        model = Part
        fields = ['name']  # Only the name field for the Part model

    def __init__(self, *args, **kwargs):
        """
        Initialize the form and limit the queryset for teams based on the current part instance.
        """
        super().__init__(*args, **kwargs)
        # Limit teams to those that can produce this part
        self.fields['teams'].queryset = Team.objects.filter(parts=self.instance)


class PartModelChoiceField(forms.ModelChoiceField):
    """
    Custom choice field for selecting Parts.
    Marks parts that are already used in any aircraft with a special label.
    """
    def label_from_instance(self, obj):
        # Check if this part is already used in any aircraft
        if AircraftPart.objects.filter(part=obj).exists():
            return f"{obj.name} (already used)"  # Indicate that the part is already in use
        return obj.name


class AircraftPartAdminForm(forms.ModelForm):
    """
    Admin form for creating or updating AircraftPart objects.
    Utilizes a custom PartModelChoiceField for part selection.
    """
    part = PartModelChoiceField(queryset=Part.objects.all(), required=True)

    class Meta:
        model = AircraftPart
        fields = '__all__'  # Include all fields from the AircraftPart model


class PersonnelAdminForm(forms.ModelForm):
    """
    Admin form for creating or updating Personnel objects.
    Includes fields for username and password for User creation.
    """
    username = forms.CharField(max_length=150, required=True, help_text="Enter the username for the Personnel")
    password = forms.CharField(widget=forms.PasswordInput, required=True,
                               help_text="Enter the password for the Personnel")

    class Meta:
        model = Personnel
        fields = ['username', 'password', 'team', 'role']  # Include relevant fields for Personnel

    def save(self, commit=True):
        """
        Override save method to create a User instance and link it to the Personnel instance.
        """
        # Create a User instance with username and password
        user = User.objects.create_user(username=self.cleaned_data['username'], password=self.cleaned_data['password'])

        # Assign the User instance to Personnel before saving
        personnel = super().save(commit=False)
        personnel.user = user

        if commit:
            personnel.save()  # Save the Personnel instance

        return personnel  # Return the created or updated Personnel instance
