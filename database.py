from sqlite3 import connect
from csv import reader


connection = connect('db.sqlite3')
cursor = connection.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS statistics(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        регион TEXT,
        школа TEXT,
        несьедаемые REAL,
        все_меню INTEGER,
        санпин REAL,
        стоимость_завтрака REAL,
        стоимость_обеда INTEGER,
        бз REAL,
        жз REAL,
        уз REAL,
        бо REAL,
        жо REAL,
        уо REAL,
        proteins_b TEXT,
        fats_b TEXT,
        carb_b TEXT,
        breakf INTEGER,
        proteins_d TEXT,
        fats_d TEXT,
        carb_d TEXT,
        dinner INTEGER
    )
    '''
)

data = []

with open('clean_data.csv', encoding='utf-8') as f:
    read = reader(f, delimiter=';')
    read.__next__()
    for line in read:
        chunk = []
        chunk.append(line[1])
        chunk.append(line[2])
        chunk.append(float(line[3]))
        chunk.append(float(line[4]))
        chunk.append(float(line[5]))
        chunk.append(float(line[6]))
        chunk.append(float(line[7]))
        chunk.append(float(line[8]))
        chunk.append(float(line[9]))
        chunk.append(float(line[10]))
        chunk.append(float(line[11]))
        chunk.append(float(line[12]))
        chunk.append(float(line[13]))
        chunk.append(line[14])
        chunk.append(line[15])
        chunk.append(line[16])
        chunk.append(int(line[17]))
        chunk.append((line[18]))
        chunk.append((line[19]))
        chunk.append((line[20]))
        chunk.append(int(line[21]))
        data.append(chunk)

with connection:
    cursor.executemany(
        '''
        INSERT INTO statistics VALUES(null, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''',
        data
    )
