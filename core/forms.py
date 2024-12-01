from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, CustomEmailValidator, Topico, Postagem, Evento, Disciplina, Notificacao
import sqlite3

class NovoTopicoForm(forms.ModelForm):
    class Meta:
        model = Topico
        fields = ['titulo', 'descricao']

class NovaPostagemForm(forms.ModelForm):
    class Meta:
        model = Postagem
        fields = ['conteudo']

class TopicoForm(forms.ModelForm):
    class Meta:
        model = Topico
        fields = ['titulo', 'descricao']
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Título do Tópico'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descrição do Tópico'}),
        }
def get_departments():
    conn = sqlite3.connect('departments.db')
    cursor = conn.cursor()
    cursor.execute("SELECT code, name FROM departments ORDER BY code")
    departments = [(f"{code} - {name}", f"{code} - {name}") for code, name in cursor.fetchall()]
    conn.close()
    return departments

def get_cursos_e_semestres():
    conn = sqlite3.connect('disciplinas_engenharia_poli_usp.db')
    cursor = conn.cursor()
    
    # Obter todos os cursos
    cursor.execute("SELECT DISTINCT curso FROM disciplinas ORDER BY curso")
    cursos = [row[0] for row in cursor.fetchall()]
    
    # Criar uma lista de semestres do 1º ao 13º
    semestres = [f"{i}º" for i in range(1, 14)]
    
    # Usar o mesmo conjunto de semestres para todos os cursos
    semestres_por_curso = {curso: semestres for curso in cursos}
    
    conn.close()
    return cursos, semestres_por_curso

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'user_type', 'curso', 'semestre', 'departamento', 'foto', 'is_public_profile']
        widgets = {
            'foto': forms.ClearableFileInput(attrs={
                'class': 'custom-file-input',
                'placeholder': 'Escolha um arquivo',
                'accept': 'image/*',
            }),
            'is_public_profile': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'foto': 'Foto de Perfil',
            'is_public_profile': 'Privacidade',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.user_type not in ['aluno', 'representante']:
            del self.fields['curso']
            del self.fields['semestre']
        if self.instance.user_type != 'professor':
            del self.fields['departamento']

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label='Nome')
    last_name = forms.CharField(max_length=30, required=True, label='Sobrenome')
    curso = forms.ChoiceField(choices=[], required=False)
    semestre = forms.ChoiceField(choices=[], required=False)
    departamento = forms.ChoiceField(choices=[], required=False)
    foto = forms.ImageField(required=False)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'user_type', 'curso', 'semestre', 'departamento', 'foto')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].validators = [CustomEmailValidator()]
        
        cursos, semestres_por_curso = get_cursos_e_semestres()
        self.fields['curso'].choices = [('', 'Selecione um curso')] + [(curso, curso) for curso in cursos]
        
        semestres = semestres_por_curso[cursos[0]] if cursos else []
        self.fields['semestre'].choices = [('', 'Selecione um semestre')] + [(sem, sem) for sem in semestres]
        
        self.fields['departamento'].choices = [('', 'Selecione um departamento')] + get_departments()
        
        self.semestres_por_curso = semestres_por_curso

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        curso = cleaned_data.get('curso')
        semestre = cleaned_data.get('semestre')
        departamento = cleaned_data.get('departamento')

        if user_type in ['aluno', 'representante']:
            if not curso:
                self.add_error('curso', 'Este campo é obrigatório para alunos e representantes.')
            if not semestre:
                self.add_error('semestre', 'Este campo é obrigatório para alunos e representantes.')
            elif curso and semestre:
                if semestre not in self.semestres_por_curso.get(curso, []):
                    self.add_error('semestre', 'Semestre inválido para o curso selecionado.')
        elif user_type == 'professor':
            if not departamento:
                self.add_error('departamento', 'Este campo é obrigatório para professores.')
        
        return cleaned_data
    

class EventoForm(forms.ModelForm):
    class Meta:
        model = Evento
        fields = ['nome', 'descricao', 'data_inicio', 'data_fim', 'local', 'imagem']
        widgets = {
            'data_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'data_fim': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class NotificationForm(forms.ModelForm):
    class Meta:
        model = Notificacao
        fields = ['titulo', 'mensagem', 'disciplina', 'evento']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Restringir escolhas com base no tipo de usuário
        if user:
            if user.user_type in ['professor', 'representante']:
                # Filtra disciplinas do professor ou representante
                self.fields['disciplina'].queryset = Disciplina.objects.filter(userdiscipline__user=user)
                self.fields['evento'].queryset = Evento.objects.none()
            elif user.user_type == 'entidade':
                # Filtra eventos criados ou geridos pela entidade
                self.fields['evento'].queryset = Evento.objects.filter(criado_por=user)
                self.fields['disciplina'].queryset = Disciplina.objects.none()

from .models import HorarioGrade

class HorarioGradeForm(forms.ModelForm):
    class Meta:
        model = HorarioGrade
        fields = ['disciplina', 'dia_da_semana', 'horario_inicio', 'horario_fim']
        widgets = {
            'horario_inicio': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
            'horario_fim': forms.TimeInput(format='%H:%M', attrs={'type': 'time', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Adiciona classe CSS para os campos, sem sobrescrever widgets personalizados
        for field_name, field in self.fields.items():
            if not isinstance(field.widget, forms.TimeInput):  # Evita sobrescrever TimeInput
                field.widget.attrs.update({"class": "form-control"})