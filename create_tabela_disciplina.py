import requests
from bs4 import BeautifulSoup
import sqlite3
import os

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

def criar_banco_dados():
    conn = sqlite3.connect('disciplinas_engenharia_poli_usp.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disciplinas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        codigo TEXT,
        semestre TEXT,
        curso TEXT,
        tipo TEXT
    )
    ''')

    conn.commit()
    return conn, cursor

def inserir_disciplinas(conn, cursor, disciplinas):
    cursor.executemany('''
    INSERT INTO disciplinas (nome, codigo, semestre, curso, tipo)
    VALUES (?, ?, ?, ?, ?)
    ''', disciplinas)
    conn.commit()

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

    conn, cursor = criar_banco_dados()

    for nome_curso, codcur, codhab in cursos:
        url = f"{base_url}?codcg=3&codcur={codcur}&codhab={codhab}&tipo=N"
        print(f"Processando: {nome_curso}")

        _, disciplinas_obrigatorias, disciplinas_optativas = extrair_disciplinas(url, nome_curso)

        disciplinas_para_inserir = []

        for semestre, disciplinas in disciplinas_obrigatorias.items():
            for disciplina in disciplinas:
                disciplinas_para_inserir.append((
                    disciplina['nome'],
                    disciplina['codigo'],
                    semestre,
                    nome_curso,
                    'Obrigatória'
                ))

        for semestre, disciplinas in disciplinas_optativas.items():
            for disciplina in disciplinas:
                disciplinas_para_inserir.append((
                    disciplina['nome'],
                    disciplina['codigo'],
                    semestre,
                    nome_curso,
                    'Optativa'
                ))

        inserir_disciplinas(conn, cursor, disciplinas_para_inserir)

    return conn, cursor

# Criar o banco de dados e inserir as disciplinas
conn, cursor = obter_todas_disciplinas()

# Exibir as primeiras 20 linhas da tabela
print("\nPrimeiras 20 linhas da tabela:")
cursor.execute("SELECT * FROM disciplinas LIMIT 20")
for row in cursor.fetchall():
    print(row)

# Algumas estatísticas básicas
print("\nEstatísticas:")
cursor.execute("SELECT COUNT(*) FROM disciplinas")
total_disciplinas = cursor.fetchone()[0]
print(f"Total de disciplinas: {total_disciplinas}")

print("\nDisciplinas por tipo:")
cursor.execute("SELECT tipo, COUNT(*) FROM disciplinas GROUP BY tipo")
for tipo, count in cursor.fetchall():
    print(f"{tipo}: {count}")

print("\nDisciplinas por curso:")
cursor.execute("SELECT curso, COUNT(*) FROM disciplinas GROUP BY curso")
for curso, count in cursor.fetchall():
    print(f"{curso}: {count}")

# Fechar a conexão com o banco de dados
conn.close()

print(f"\nBanco de dados criado: {os.path.abspath('disciplinas_engenharia_poli_usp.db')}")