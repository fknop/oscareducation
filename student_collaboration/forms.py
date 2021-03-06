from django import forms
from django.forms import IntegerField, NumberInput

from .models import StudentCollaborator, CollaborativeSettings, HelpRequest


class StudentCollaboratorForm(forms.ModelForm):
    class Meta:
        model = StudentCollaborator
        fields = ['collaborative_tool', 'postal_code']
        # collaborative_tool = forms.CheckboxInput
        # postal_code = forms.Select

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('skills', None)
        super(StudentCollaboratorForm, self).__init__(*args, **kwargs)
        self.fields['collaborative_tool'].widget.attrs.update({'class' : 'form-control', 'id': 'collaborative_tool_check'})
        self.fields['postal_code'].widget.attrs.update({'class': 'form-control'})


class CollaborativeSettingsForm(forms.ModelForm):
    class Meta:
        model = CollaborativeSettings
        fields = ['distance']
        widgets = {
            'distance': NumberInput(attrs={'min':0,'max': '100'})
        }
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('skills', None)
        super(CollaborativeSettingsForm, self).__init__(*args, **kwargs)
        self.fields['distance'].widget.attrs.update({'class' : 'form-control'})


class UnmasteredSkillsForm(forms.Form):

    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('skills', None)
        self.current_user = kwargs.pop('current_user', None)
        self.too_many_requests = kwargs.pop('too_many_requests', False)
        super(UnmasteredSkillsForm, self).__init__(*args, **kwargs)
        self.fields['list'] = forms.ModelMultipleChoiceField(queryset=qs, label="")
        self.fields['list'].widget.attrs.update({'id' : 'unmastered-skill-select', 'multiple' : 'multiple'})

    # custom method to do validation
    # https://docs.djangoproject.com/fr/1.11/ref/forms/validation/#cleaning-a-specific-field-attribute
    def clean_list(self):
        skills = self.cleaned_data['list']
        return skills


class SkillsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        qs = kwargs.pop('skills', None)
        self.current_user = kwargs.pop('current_user', None)
        super(SkillsForm, self).__init__(*args, **kwargs)
        self.fields['list'] = forms.ModelChoiceField(queryset=qs, label="")


class HelpRequestForm(forms.Form):
    def __init__(self, *args, **kwargs):
        helprequest = kwargs.pop('HelpRequests')
        super(HelpRequestForm, self).__init__(*args, **kwargs)
        for q in helprequest:
            self.fields['HelpRequests'] = forms.CharField(label=HelpRequest.skill)
