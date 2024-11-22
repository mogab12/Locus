import os
import django
import requests
from bs4 import BeautifulSoup

# Configurar o ambiente Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Disciplina

def extrair_disciplinas(url, nome_curso):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    disciplinas_obrigatorias = {}
    disciplinas_optativas = {}
    current_section = "obrigatoria"
    current_semestre = None

    for elemento in soup.find_all(['tr', 'td']):
        if elemento.name == 'td' and elemento.get('colspan') == '9' and elemento.find('b'):
            texto = elemento.get_text(strip=True)
            if "Disciplinas Optativas" in texto:
                current_section = "optativa"
                current_semestre = None
        elif elemento.get('bgcolor') == '#CCCCCC':
            current_semestre = elemento.get_text(strip=True).split('Período')[0].strip()
            if current_semestre != "Sem período definido":
                if current_section == "obrigatoria":
                    disciplinas_obrigatorias[current_semestre] = []
                else:
                    disciplinas_optativas[current_semestre] = []
        elif elemento.find_all('td') and len(elemento.find_all('td')) >= 5:
            colunas = elemento.find_all('td')
            codigo = colunas[0].text.strip()
            nome = colunas[1].text.strip()
            
            if codigo.lower() == 'subtotal:':
                continue
            
            disciplina = {
                'codigo': codigo,
                'nome': nome,
            }

            if current_section == "obrigatoria" and current_semestre and current_semestre != "Sem período definido":
                disciplinas_obrigatorias[current_semestre].append(disciplina)
            elif current_section == "optativa" and current_semestre and current_semestre != "Sem período definido":
                disciplinas_optativas[current_semestre].append(disciplina)

    return nome_curso, disciplinas_obrigatorias, disciplinas_optativas

def inserir_disciplinas(nome_curso, disciplinas_obrigatorias, disciplinas_optativas):
    disciplinas_para_inserir = []

    for semestre, disciplinas in disciplinas_obrigatorias.items():
        for disciplina in disciplinas:
            disciplinas_para_inserir.append(
                Disciplina(
                    nome=disciplina['nome'],
                    codigo=disciplina['codigo'],
                    semestre=semestre,
                    curso=nome_curso,
                    tipo='Obrigatória'
                )
            )

    for semestre, disciplinas in disciplinas_optativas.items():
        for disciplina in disciplinas:
            disciplinas_para_inserir.append(
                Disciplina(
                    nome=disciplina['nome'],
                    codigo=disciplina['codigo'],
                    semestre=semestre,
                    curso=nome_curso,
                    tipo='Optativa'
                )
            )
    
    # Usar o Django ORM para salvar em massa
    Disciplina.objects.bulk_create(disciplinas_para_inserir)

def obter_todas_disciplinas():
    cursos = [
        ("Engenharia Ambiental", "3151", "3000"),
        ("Engenharia Civil", "3022", "3000"),
        ("Engenharia de Computação", "3122", "3000"),
        ("Engenharia de Materiais", "3102", "3000"),
        ("Engenharia de Minas", "3052", "3000"),
        ("Engenharia de Petróleo", "3056", "3000"),
        ("Engenharia de Produção", "3083", "3000"),
        ("Engenharia Elétrica - Ênfase em Automação e Controle", "3032", "3150"),
        ("Engenharia Elétrica - Ênfase em Eletrônica e Sistemas Computacionais", "3032", "3180"),
        ("Engenharia Elétrica - Ênfase em Energia e Automação Elétricas", "3032", "3190"),
        ("Engenharia Elétrica - Ênfase em Telecomunicações", "3032", "3160"),
        ("Engenharia Mecânica", "3044", "3000"),
        ("Engenharia Mecatrônica", "3112", "3000"),
        ("Engenharia Metalúrgica", "3062", "3000"),
        ("Engenharia Naval", "3072", "3000"),
        ("Engenharia Nuclear", "3190", "3000"),
        ("Engenharia Química", "3092", "3000")
    ]

    base_url = "https://uspdigital.usp.br/jupiterweb/listarGradeCurricular"

    for nome_curso, codcur, codhab in cursos:
        url = f"{base_url}?codcg=3&codcur={codcur}&codhab={codhab}&tipo=N"
        print(f"Processando: {nome_curso}")

        nome_curso, disciplinas_obrigatorias, disciplinas_optativas = extrair_disciplinas(url, nome_curso)

        inserir_disciplinas(nome_curso, disciplinas_obrigatorias, disciplinas_optativas)

# Executar o script para salvar disciplinas
obter_todas_disciplinas()