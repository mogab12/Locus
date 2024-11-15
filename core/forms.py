from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, CustomEmailValidator

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'user_type', 'curso', 'semestre', 'foto']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user_type not in ['aluno', 'representante']:
            del self.fields['curso']
            del self.fields['semestre']

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    curso = forms.CharField(max_length=100, required=False)
    semestre = forms.IntegerField(required=False)
    foto = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'curso', 'semestre', 'foto')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].validators = [CustomEmailValidator()]

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