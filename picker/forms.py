from django import forms
from picker.models import Team

class GameForm(forms.Form):
    redTeam = forms.ModelChoiceField(queryset=Team.objects.all())
    blueTeam = forms.ModelChoiceField(queryset=Team.objects.all())
