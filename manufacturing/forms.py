from django import forms

from manufacturing.models import Part, Team


class PartForm(forms.ModelForm):
    class Meta:
        model = Part
        fields = ['name', 'teams']  # Assuming you have a field to choose the teams

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Limit teams to those that can produce this part
        self.fields['teams'].queryset = Team.objects.filter(parts=self.instance)
