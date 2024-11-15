from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    curso = forms.CharField(max_length=100, required=False)
    semestre = forms.IntegerField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('user_type', 'curso', 'semestre')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['curso'].widget.attrs.update({'class': 'form-control'})
        self.fields['semestre'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        curso = cleaned_data.get('curso')
        semestre = cleaned_data.get('semestre')

        if user_type in ['aluno', 'representante']:
            if not curso:
                self.add_error('curso', 'Este campo é obrigatório para alunos e representantes.')
            if not semestre:
                self.add_error('semestre', 'Este campo é obrigatório para alunos e representantes.')
        
        return cleaned_data