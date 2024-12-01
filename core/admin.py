from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Salas



class SalasAdmin(admin.ModelAdmin):
    model = Salas
    list_display = ['nome_sala', 'posição_x', 'posição_y']  
    search_fields = ['nome_sala']  
    list_filter = ['nome_sala']  
    fieldsets = (
        (None, {'fields': ('nome_sala',)}),
        ('Posição no Mapa', {'fields': ('posição_x', 'posição_y')}),
    )


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
admin.site.register(Salas, SalasAdmin)
