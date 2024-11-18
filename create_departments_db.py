import sqlite3

departments = [
    ('PSI', 'Eng de Sistemas Eletrônicos'),
    ('PMR', 'Eng Mecatrônica Sist Mecânicos'),
    ('PTC', 'Eng Telecomunicações e Controle'),
    ('PCS', 'Engenharia de Comp e Sist Digitais'),
    ('PCC', 'Engenharia de Construção Civil'),
    ('PEA', 'Engenharia de Energia e Automação Elétricas'),
    ('PEF', 'Engenharia de Estruturas e Geotécnica'),
    ('PMI', 'Engenharia de Minas e de Petróleo'),
    ('PRO', 'Engenharia de Produção'),
    ('PTR', 'Engenharia de Transportes'),
    ('PHA', 'Engenharia Hidráulica e Ambiental'),
    ('PHD', 'Engenharia Hidráulica e Sanitária'),
    ('PME', 'Engenharia Mecânica'),
    ('PMT', 'Engenharia Metalúrgica e Materiais'),
    ('PNV', 'Engenharia Naval e Oceânica'),
    ('PQI', 'Engenharia Química'),
]

conn = sqlite3.connect('departments.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS departments (
    code TEXT PRIMARY KEY,
    name TEXT NOT NULL
)
''')

cursor.executemany('INSERT OR REPLACE INTO departments (code, name) VALUES (?, ?)', departments)

conn.commit()
conn.close()

print("Banco de dados de departamentos criado com sucesso.")