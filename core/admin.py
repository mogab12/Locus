from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Mapas

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'get_full_name', 'user_type', 'curso', 'semestre', 'is_staff']
    list_filter = ['user_type', 'is_staff', 'is_superuser']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('first_name', 'last_name', 'email', 'foto')}),
        ('Informações Acadêmicas', {'fields': ('user_type', 'curso', 'semestre')}),
        ('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Datas Importantes', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'first_name', 'last_name', 'user_type', 'curso', 'semestre', 'foto'),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Mapas)