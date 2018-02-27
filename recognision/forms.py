from django import forms
from django.db.models import Q

from .models import Algorithm, History

class AlgorithmCreationForm(forms.Form):
    name = forms.CharField(max_length=256)
    positive_files = forms.FileField(widget=forms.FileInput(attrs={'multiple':None}), required=False)
    positive_url = forms.URLField(required=False)
    negative_url = forms.URLField()

    def clean(self):
        positive_files = self.cleaned_data.get('positive_files')
        positive_url = self.cleaned_data.get('positive_url')
        files_exist = url_exist = False
        if positive_files:
            files_exist = True
        if positive_url:
            url_exist = True
        if not files_exist ^ url_exist:
            raise forms.ValidationError("You should choose only url or file uploading way")
        return self.cleaned_data


class TestAlgorithmCreationForm(forms.Form):
    name = forms.CharField(max_length=256)
    algorithm_choice = forms.ChoiceField(choices=())
    input_images = forms.FileField(widget=forms.FileInput(attrs={'multiple':None}))

    def __init__(self, *args, user, **kwargs):
        print(user)
        super(TestAlgorithmCreationForm, self).__init__(*args, **kwargs)
        qs = Algorithm.objects.filter(
            Q(type='CUSTOM') & Q(owner=user) |
            Q(type='BASE')
        )
        self.fields['algorithm_choice'] = forms.ChoiceField(choices=[(str(i.id), i.name) for i in qs])