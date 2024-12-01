from datetime import datetime, timedelta

from django.utils import timezone
from core.models import HorarioGrade

def proxima_aula_função(usuario):
    agora = timezone.localtime(timezone.now())
    #dia_atual = agora.weekday()
    dia_atual = 0
    hora_atual = agora.time()

    aulas = HorarioGrade.objects.filter(usuario = usuario).order_by('dia_da_semana','horario_inicio')

    dias_da_semana = {
        'SEG' : 0 ,
        'TER' : 1 ,
        'QUA' : 2 ,
        'QUI' : 3 ,
        'SEX' : 4 ,
        'SAB' : 5 ,
        'DOM' : 6 ,
    }

    proxima = None
    
    for aula in aulas:
        
        dia_semana = dias_da_semana[aula.dia_da_semana]
        
        if dia_semana > dia_atual or (dia_semana == dia_atual and aula.horario_inicio > hora_atual):
            if proxima is None or (dia_semana < dias_da_semana[proxima.dia_da_semana] or (dia_semana == dias_da_semana[proxima.dia_da_semana] and aula.horario_inicio < proxima.horario_inicio)):
                proxima = aula
    

    return proxima
       